import os
from fastapi.testclient import TestClient
from modules.forensics.db import ForensicsDB
from interface.api import app


def test_create_and_use_db_admin(tmp_path, monkeypatch):
    # Use a temporary working directory so the SQLite DB is isolated
    monkeypatch.chdir(tmp_path)
    # Set an initial root token via env so we can create the first DB admin
    monkeypatch.setenv('ADMIN_API_TOKEN', 'ROOT')

    client = TestClient(app)

    # Access admins page with root token
    r = client.get('/admin/admins', headers={'Authorization': 'Bearer ROOT'})
    assert r.status_code == 200

    # Create a new admin with a token
    r = client.post('/admin/admins', data={'name': 'Alice', 'token': 'NEWTOKEN'}, headers={'Authorization': 'Bearer ROOT'}, follow_redirects=False)
    assert r.status_code in (302, 303)
    # Redirect location should include the created token so it can be shown to the creator once
    assert 'Location' in r.headers
    assert 'created_token=NEWTOKEN' in r.headers['Location']

    # Fetch admins page and ensure token is rendered with a copy button
    r2 = client.get('/admin/admins', headers={'Authorization': 'Bearer ROOT'})
    assert r2.status_code == 200
    assert 'NEWTOKEN' in r2.text
    assert 'data-token="NEWTOKEN"' in r2.text

    # Check DB contains the admin
    db = ForensicsDB()
    db.init_tables()
    admins = db.list_admins()
    tokens = [a['token'] for a in admins]
    assert 'NEWTOKEN' in tokens
    admin_id = admins[0]['id']

    # Remove env token so only DB token is valid
    monkeypatch.delenv('ADMIN_API_TOKEN', raising=False)

    # Use new DB token to access /admin (dashboard)
    r = client.get('/admin/', headers={'Authorization': 'Bearer NEWTOKEN'})
    assert r.status_code == 200

    # Delete the admin while authenticated with the same DB token
    r = client.post(f'/admin/admins/{admin_id}/delete', headers={'Authorization': 'Bearer NEWTOKEN'}, follow_redirects=False)
    assert r.status_code in (302, 303)

    # Ensure admin removed
    admins2 = db.list_admins()
    assert all(a['id'] != admin_id for a in admins2)

    # Now the token should no longer work
    r = client.get('/admin/', headers={'Authorization': 'Bearer NEWTOKEN'})
    assert r.status_code in (401, 302)
