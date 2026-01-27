import os
from fastapi.testclient import TestClient
from interface.api import app

client = TestClient(app)


def test_admin_requires_token_and_login(monkeypatch):
    monkeypatch.setenv('ADMIN_API_TOKEN', 'SECRET')

    # Without token -> login page
    r = client.get('/admin')
    assert r.status_code == 401
    assert 'Admin Login' in r.text

    # Wrong token via header
    r2 = client.get('/admin', headers={'Authorization': 'Bearer WRONG'})
    assert r2.status_code == 401

    # Correct token via header
    r3 = client.get('/admin', headers={'Authorization': 'Bearer SECRET'})
    assert r3.status_code == 200
    assert 'Dashboard' in r3.text

    # Login via form and cookie
    r4 = client.post('/admin/login', data={'token': 'SECRET'}, follow_redirects=False)
    assert r4.status_code in (302, 307)
    assert 'set-cookie' in r4.headers
    cookie = r4.headers.get('set-cookie')

    # Use cookie to access
    r5 = client.get('/admin', headers={'cookie': cookie})
    assert r5.status_code == 200
    assert 'Dashboard' in r5.text
