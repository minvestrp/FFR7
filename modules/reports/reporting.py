"""Примитивные функции для экспорта отчётов (JSON/PDF stub).
"""
import json
from typing import Any


def export_investigation_json(db, investigation_id: int, out_path: str) -> None:
    """Экспорт расследования (JSON) из ForensicsDB в файл."""
    data = db.get_investigation(investigation_id)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def export_investigation_pdf(db, investigation_id: int, out_path: str) -> None:
    """Заглушка: экспорт в PDF (реализация планируется).
    Можно использовать reportlab / weasyprint / wkhtmltopdf.
    """
    raise NotImplementedError("PDF export not implemented. Use JSON export for now.")


def export_graph_from_db(db, investigation_id: int, out_path: str, fmt: str = "png") -> None:
    """Построить граф из расследования и экспортировать изображение."""
    from modules.forensics.db import ForensicsDB
    from .graph import build_graph_from_edges, export_graph_image

    # DB instance may be passed as object; handle both
    if isinstance(db, ForensicsDB):
        data = db.get_investigation(investigation_id)
    else:
        # accept db as path
        db = ForensicsDB(db)
        data = db.get_investigation(investigation_id)

    edges = data.get("edges", [])
    g = build_graph_from_edges(edges)
    export_graph_image(g, out_path, fmt)


def render_investigation_html(db, investigation_id: int) -> str:
    """Render investigation HTML using Jinja2 template and return HTML string."""
    try:
        from jinja2 import Environment, FileSystemLoader, select_autoescape
    except Exception:
        raise RuntimeError("Jinja2 is required for PDF export. Install jinja2.")
    from modules.forensics.db import ForensicsDB
    import os

    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )
    tpl = env.get_template("investigation.html.j2")

    if isinstance(db, ForensicsDB):
        data = db.get_investigation(investigation_id)
    else:
        db = ForensicsDB(db)
        data = db.get_investigation(investigation_id)

    html = tpl.render(investigation=data["investigation"], edges=data["edges"])
    return html


# Provide a module-level HTML symbol to allow tests to monkeypatch the behavior
try:
    from weasyprint import HTML  # type: ignore
except Exception:
    HTML = None


def export_investigation_pdf(db, investigation_id: int, out_path: str) -> None:
    """Экспорт расследования в PDF. Использует WeasyPrint (HTML -> PDF) через Jinja2 шаблон."""
    if HTML is None:
        raise RuntimeError("WeasyPrint is required for PDF export. Install weasyprint and its system deps.")

    html = render_investigation_html(db, investigation_id)
    HTML(string=html).write_pdf(out_path)
