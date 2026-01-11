import tempfile
import os
from unittest import mock

from modules.storage import ipfs as ipfs_mod


def test_ipfs_upload_raises_when_no_method(monkeypatch, tmp_path):
    # Ensure no PINATA env
    monkeypatch.delenv('PINATA_API_KEY', raising=False)
    monkeypatch.delenv('PINATA_SECRET', raising=False)

    # Ensure ipfshttpclient not available and ipfs CLI not available
    monkeypatch.setattr(ipfs_mod, 'shutil_which', lambda cmd: False)
    # Create a temporary file
    f = tmp_path / "t.txt"
    f.write_text("hello")

    try:
        ipfs_mod.upload_file_to_ipfs(str(f))
        assert False, "Should have raised"
    except RuntimeError as e:
        assert 'No IPFS upload method available' in str(e)


def test_ipfs_upload_pinata(monkeypatch, tmp_path):
    # Fake Pinata response
    monkeypatch.setenv('PINATA_API_KEY', 'K')
    monkeypatch.setenv('PINATA_SECRET', 'S')
    tmp = tmp_path / "r.txt"
    tmp.write_text("data")

    def fake_post(url, files, headers, timeout):
        class R:
            def raise_for_status(self):
                pass
            def json(self):
                return {"IpfsHash": "QmFAKE"}
        return R()

    monkeypatch.setattr('modules.storage.ipfs.requests.post', fake_post)
    res = ipfs_mod.upload_file_to_ipfs(str(tmp))
    assert res.get('hash') == 'QmFAKE'
