from fastapi.testclient import TestClient
from interface.api import app


def test_create_and_export(monkeypatch, tmp_path):
    # Monkeypatch TraceAnalyzer.analyze_and_store to create a dummy invest
    def fake_analyze_and_store(self, address, db, build_graph=False):
        return 999

    monkeypatch.setattr('modules.forensics.trace_analyzer.TraceAnalyzer.analyze_and_store', fake_analyze_and_store)
    # Ensure TraceAnalyzer can be constructed
    monkeypatch.setenv('ETHERSCAN_API_KEY', 'DUMMY')

    client = TestClient(app)
    r = client.post('/investigations', json={'address': '0xSOMEADDR'})
    assert r.status_code == 200
    assert r.json().get('investigation_id') == 999

    # Export (will fail because DB won't have id 999) — check proper error handling
    r2 = client.get('/investigations/999/export')
    assert r2.status_code == 400
