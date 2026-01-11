"""REST API заглушка на FastAPI для доступа к анализаторам"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from modules.analyzer import analyze_contract_from_path
from modules.forensics import TraceAnalyzer

app = FastAPI(title="SmartSec API")

# Mount admin UI router (server-side templates)
from . import admin as admin_router
app.include_router(admin_router.router)

# Mount static files for admin (simple)
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="./data"), name="static")

class ContractPayload(BaseModel):
    path: str

class AddressPayload(BaseModel):
    address: str


@app.post("/analyze/contract")
def analyze_contract(payload: ContractPayload):
    res = analyze_contract_from_path(payload.path)
    return res


@app.post("/forensics/trace")
def trace_address(payload: AddressPayload):
    try:
        ta = TraceAnalyzer()
        res = ta.analyze_address(payload.address)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post('/investigations')
def create_investigation(payload: AddressPayload):
    """Создать расследование по адресу и вернуть id"""
    try:
        ta = TraceAnalyzer()
        from modules.forensics.db import ForensicsDB
        db = ForensicsDB()
        db.init_tables()
        inv_id = ta.analyze_and_store(payload.address, db)
        return {"investigation_id": inv_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get('/investigations/{inv_id}/export')
def export_investigation(inv_id: int, format: str = 'json'):
    try:
        from modules.forensics.db import ForensicsDB
        from modules.reports.reporting import export_investigation_json
        db = ForensicsDB()
        if format != 'json':
            raise HTTPException(status_code=400, detail='Only json export supported')
        out = f"investigation_{inv_id}.json"
        export_investigation_json(db, inv_id, out)
        return {"exported": out}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
