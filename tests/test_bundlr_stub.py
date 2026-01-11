import os
import pytest
from modules.storage import bundlr


def test_bundlr_requires_config(monkeypatch):
    monkeypatch.delenv('BUNDLR_URL', raising=False)
    monkeypatch.delenv('BUNDLR_PRIVATE_KEY', raising=False)
    with pytest.raises(ValueError):
        bundlr.upload_file_to_bundlr('/tmp/nonexistent')


def test_bundlr_delegation(monkeypatch, tmp_path):
    # Provide fake env
    monkeypatch.setenv('BUNDLR_URL', 'https://node.test')
    monkeypatch.setenv('BUNDLR_PRIVATE_KEY', 'fakekey')

    # Monkeypatch internal _upload_via_client
    def fake_upload(path, url, key, currency):
        return {'tx_id': 'FAKE_TX'}
    monkeypatch.setattr(bundlr, '_upload_via_client', fake_upload)

    tmp = tmp_path / 'f.txt'
    tmp.write_text('x')
    res = bundlr.upload_file_to_bundlr(str(tmp))
    assert res.get('tx_id') == 'FAKE_TX'
