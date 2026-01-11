import tempfile
import os
from modules.forensics.db import ForensicsDB
from modules.reports.reporting import export_investigation_pdf


def test_pdf_export_monkeypatched_weasyprint(monkeypatch, tmp_path):
    # Prepare DB with one investigation
    tf = tmp_path / "db.sqlite"
    db = ForensicsDB(str(tf))
    db.init_tables()
    inv_id = db.add_investigation('0xA', notes='test')
    db.add_edge(inv_id, '0xA', '0xB', '100', '0xTX', '2020-01-01T00:00:00')

    out = tmp_path / 'report.pdf'

    class FakeHTML:
        def __init__(self, string=None):
            self.string = string
        def write_pdf(self, out_path):
            with open(out_path, 'wb') as f:
                f.write(b'%PDF-1.4 fake')

    monkeypatch.setattr('modules.reports.reporting.HTML', FakeHTML)

    export_investigation_pdf(db, inv_id, str(out))
    assert out.exists()
    # Basic PDF magic header
    with open(out, 'rb') as f:
        data = f.read(8)
        assert data.startswith(b'%PDF')
