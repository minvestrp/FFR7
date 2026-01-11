"""IPFS uploader helper. Supports Pinata (if PINATA_API_KEY set), ipfshttpclient, or ipfs CLI as fallbacks."""
import os
import requests
import subprocess
from typing import Dict

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET = os.getenv("PINATA_SECRET")


def upload_file_to_ipfs(path: str) -> Dict[str, str]:
    """Upload a file to IPFS and return a dict with at least {'hash': <cid>}.

    Tries in order:
    - Pinata (if API keys provided)
    - ipfshttpclient (python lib)
    - ipfs CLI (`ipfs add -Q`)

    Raises RuntimeError if none available.
    """
    if PINATA_API_KEY and PINATA_SECRET:
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        headers = {
            "pinata_api_key": PINATA_API_KEY,
            "pinata_secret_api_key": PINATA_SECRET,
        }
        with open(path, "rb") as f:
            files = {"file": (os.path.basename(path), f)}
            r = requests.post(url, files=files, headers=headers, timeout=60)
            r.raise_for_status()
            j = r.json()
            cid = j.get("IpfsHash") or j.get("IpfsHash")
            return {"hash": cid}

    # Try ipfshttpclient
    try:
        import ipfshttpclient

        client = ipfshttpclient.connect()
        res = client.add(path)
        cid = res.get("Hash") if isinstance(res, dict) else getattr(res, "Hash", None)
        return {"hash": cid}
    except Exception:
        pass

    # Try ipfs CLI
    if shutil_which("ipfs"):
        try:
            out = subprocess.check_output(["ipfs", "add", "-Q", path], stderr=subprocess.STDOUT)
            cid = out.decode().strip()
            return {"hash": cid}
        except Exception as e:
            raise RuntimeError(f"ipfs CLI failed: {e}")

    raise RuntimeError("No IPFS upload method available (set PINATA_API_KEY or install ipfshttpclient/ipfs CLI)")


def shutil_which(cmd: str) -> bool:
    """Small shim for shutil.which (avoid extra import here)."""
    try:
        from shutil import which

        return which(cmd) is not None
    except Exception:
        return False
