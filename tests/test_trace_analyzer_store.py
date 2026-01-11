import tempfile
import os
from modules.forensics.trace_analyzer import TraceAnalyzer
from modules.forensics.db import ForensicsDB


def test_analyze_and_store(monkeypatch):
    # Prepare fake txs
    fake_txs = [
        {"from": "0xA", "to": "0xB", "value": "100", "hash": "0xTX1", "timeStamp": "1600000000"},
        {"from": "0xB", "to": "0xC", "value": "200", "hash": "0xTX2", "timeStamp": "1600003600"},
    ]

    ta = TraceAnalyzer(api_key="DUMMY")
    monkeypatch.setattr(ta, 'fetch_txs', lambda address, page_size=1000: fake_txs)

    tf = tempfile.NamedTemporaryFile(delete=False)
    tf.close()
    db_path = tf.name
    try:
        db = ForensicsDB(db_path)
        db.init_tables()
        inv_id = ta.analyze_and_store('0xSOMEADDR', db)
        assert isinstance(inv_id, int)
        data = db.get_investigation(inv_id)
        assert data['investigation']['address'] == '0xSOMEADDR'
        assert len(data['edges']) == 2
    finally:
        try:
            os.unlink(db_path)
        except Exception:
            pass
