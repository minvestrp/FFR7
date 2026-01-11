from fastapi.testclient import TestClient
from interface.api import app
from modules.forensics.db import ForensicsDB

client = TestClient(app)


def test_admin_dashboard_and_list(monkeypatch, tmp_path):
    # Set admin token for auth
    monkeypatch.setenv('ADMIN_API_TOKEN', 'TEST')
    headers = {'Authorization': 'Bearer TEST'}

    r = client.get('/admin', headers=headers)
    assert r.status_code == 200
    assert 'Dashboard' in r.text

    r2 = client.get('/admin/investigations', headers=headers)
    assert r2.status_code == 200
    assert 'Investigations' in r2.text


def test_investigation_detail_flow(tmp_path):
    # Create DB and insert an investigation to be visible in admin
    db_path = tmp_path / 'testdb.sqlite'
    db = ForensicsDB(str(db_path))
    db.init_tables()
    inv_id = db.add_investigation('0xTEST', notes='from test')
    db.add_edge(inv_id, '0xA', '0xB', '10', '0xTX', '2020-01-01T00:00:00')

    # Monkeypatch ForensicsDB used by admin by replacing constructor to open our db
    original_ctor = ForensicsDB.__init__
    try:
        def fake_init(self, path: str = None):
            # call original init but set path to our tmp db
            original_ctor(self, str(db_path))
        ForensicsDB.__init__ = fake_init

        r = client.get(f'/admin/investigations/{inv_id}')
        assert r.status_code == 200
        assert 'Investigation' in r.text
        assert '0xTEST' in r.text
    finally:
        ForensicsDB.__init__ = original_ctor
