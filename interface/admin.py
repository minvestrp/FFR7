"""Admin UI (FastAPI) — simple server-side rendered pages for investigations."""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from modules.forensics.db import ForensicsDB
from modules.reports.reporting import export_investigation_json, export_investigation_pdf, export_graph_from_db
import os

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

DATA_DIR = os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)


def _extract_token_from_request(request: Request) -> str | None:
    """Robustly extract a bearer token from header, cookies, or query.

    Handles header case-insensitivity and raw scope headers for edge cases in tests.
    """
    # Header: Authorization: Bearer <token>
    auth = request.headers.get("Authorization") or request.headers.get("authorization")
    candidate = None
    if auth and isinstance(auth, str) and auth.startswith("Bearer "):
        candidate = auth.split(" ", 1)[1]

    # Fallback: raw scope headers (bytes)
    if not candidate:
        for k, v in request.scope.get("headers", []):
            try:
                if k.decode().lower() == "authorization":
                    s = v.decode()
                    if s.startswith("Bearer "):
                        candidate = s.split(" ", 1)[1]
                        break
            except Exception:
                continue

    # Cookie
    if not candidate:
        candidate = request.cookies.get("admin_token")
    # Query param (convenience)
    if not candidate:
        candidate = request.query_params.get("token")

    return candidate


def _is_authenticated(request: Request) -> bool:
    """Check request for valid admin token in header, cookie, or query param.

    Tokens are accepted from either the ENV `ADMIN_API_TOKEN` or from the `admins`
    table in the Forensics DB (token lookup). If neither exist, access is denied.
    """
    token_env = os.getenv("ADMIN_API_TOKEN")
    candidate = _extract_token_from_request(request)

    if not candidate:
        return False

    # First check ENV token if configured
    if token_env and candidate == token_env:
        return True

    # Fall back to DB-based admin tokens
    try:
        with ForensicsDB() as db:
            a = db.get_admin_by_token(candidate)
            return a is not None
    except Exception:
        # On error, deny access
        return False


@router.get("/")
def dashboard(request: Request):
    # Require auth for admin UI
    if not _is_authenticated(request):
        return templates.TemplateResponse("login.html", {"request": request}, status_code=401)

    with ForensicsDB() as db:
        db.init_tables()
        invs = db.list_investigations(limit=10)
        total = len(invs)
    return templates.TemplateResponse("dashboard.html", {"request": request, "total": total, "invs": invs})


@router.get("/login")
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login_post(request: Request):
    # Accept form field 'token'
    try:
        form = await request.form()
        token = form.get('token')
    except Exception:
        token = None

    token_env = os.getenv("ADMIN_API_TOKEN")
    if not token_env:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Admin token not configured."}, status_code=500)

    if token == token_env:
        # Set cookie and redirect
        resp = RedirectResponse(url="/admin", status_code=302)
        # HttpOnly cookie, secure flag off by default to ease local usage; set secure=True in production
        resp.set_cookie("admin_token", token_env, httponly=True, secure=False, samesite='Lax')
        return resp
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid token"}, status_code=401)



@router.get("/investigations")
def list_investigations(request: Request):
    if not _is_authenticated(request):
        return templates.TemplateResponse("login.html", {"request": request}, status_code=401)

    with ForensicsDB() as db:
        db.init_tables()
        invs = db.list_investigations(limit=100)
    return templates.TemplateResponse("investigations.html", {"request": request, "invs": invs})


@router.get("/investigations/{inv_id}")
def view_investigation(request: Request, inv_id: int):
    if not _is_authenticated(request):
        return templates.TemplateResponse("login.html", {"request": request}, status_code=401)

    with ForensicsDB() as db:
        try:
            data = db.get_investigation(inv_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Investigation not found")

        # Prepare export file paths
        json_path = os.path.join(DATA_DIR, f"investigation_{inv_id}.json")
        pdf_path = os.path.join(DATA_DIR, f"investigation_{inv_id}.pdf")
        graph_path = os.path.join(DATA_DIR, f"investigation_{inv_id}.png")

        # Ensure exports exist (generate on demand)
        try:
            export_investigation_json(db, inv_id, json_path)
        except Exception:
            json_path = None

        try:
            export_investigation_pdf(db, inv_id, pdf_path)
        except Exception:
            pdf_path = None

        try:
            export_graph_from_db(db, inv_id, graph_path, fmt="png")
        except Exception:
            graph_path = None

    return templates.TemplateResponse("investigation_detail.html", {"request": request, "data": data, "json_path": json_path, "pdf_path": pdf_path, "graph_path": graph_path})


@router.get('/download/json/{inv_id}')
def download_json(request: Request, inv_id: int):
    if not _is_authenticated(request):
        raise HTTPException(status_code=401)
    path = os.path.join(DATA_DIR, f"investigation_{inv_id}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404)
    return FileResponse(path, media_type='application/json', filename=os.path.basename(path))


@router.get('/download/pdf/{inv_id}')
def download_pdf(request: Request, inv_id: int):
    if not _is_authenticated(request):
        raise HTTPException(status_code=401)
    path = os.path.join(DATA_DIR, f"investigation_{inv_id}.pdf")
    if not os.path.exists(path):
        raise HTTPException(status_code=404)
    return FileResponse(path, media_type='application/pdf', filename=os.path.basename(path))


@router.get('/admins')
def list_admins(request: Request):
    if not _is_authenticated(request):
        return templates.TemplateResponse("login.html", {"request": request}, status_code=401)

    with ForensicsDB() as db:
        db.init_tables()
        admins = db.list_admins(limit=100)
    return templates.TemplateResponse("admins.html", {"request": request, "admins": admins})


@router.post('/admins')
async def create_admin(request: Request):
    if not _is_authenticated(request):
        return templates.TemplateResponse("login.html", {"request": request}, status_code=401)
    form = await request.form()
    name = form.get('name', '').strip() or None
    token = form.get('token', '').strip() or None
    # Generate a token if not provided
    if not token:
        import secrets

        token = secrets.token_urlsafe(32)
    with ForensicsDB() as db:
        db.init_tables()
        admin_id = db.add_admin(name=name, token=token)
    # Redirect to admins listing and include the created token so it can be shown prominently
    resp = RedirectResponse(url=f"/admin/admins?created_token={token}", status_code=302)
    return resp


@router.post('/admins/{admin_id}/delete')
def delete_admin(request: Request, admin_id: int):
    # Re-check token explicitly to avoid edge cases with request handling
    # Extract token similarly to _is_authenticated
    token_env = os.getenv("ADMIN_API_TOKEN")
    candidate = _extract_token_from_request(request)
    if not candidate:
        return templates.TemplateResponse("login.html", {"request": request}, status_code=401)

    if token_env and candidate == token_env:
        authorized = True
    else:
        try:
            with ForensicsDB() as db:
                admins_here = db.list_admins()
                a = db.get_admin_by_token(candidate)
                authorized = a is not None
        except Exception:
            authorized = False

    if not authorized:
        print(f"DEBUG: delete_admin unauthorized. candidate={candidate}, token_env={token_env}")
        return templates.TemplateResponse("login.html", {"request": request}, status_code=401)

    # Perform deletion
    try:
        with ForensicsDB() as db:
            db.init_tables()
            db.delete_admin(admin_id)
    except Exception as e:
        print(f"DEBUG: delete_admin exception: {e}")
        return templates.TemplateResponse("login.html", {"request": request}, status_code=500)

    resp = RedirectResponse(url="/admin/admins", status_code=302)
    return resp
