"""Bundlr integration helper (stub + safe wrapper).

This module provides a simple, well-documented wrapper to upload files via Bundlr
(or other Arweave relayers) when a proper client is installed. The implementation
is intentionally conservative: if a Bundlr Python client is available it will be
used; otherwise the module exposes a clear API and helpful error messages so
users can configure the environment and install the required deps.

Environment variables:
- BUNDLR_URL (optional) — URL of Bundlr node (e.g., https://node1.bundlr.network)
- BUNDLR_PRIVATE_KEY (required) — private key (or path to key) used to sign uploads
- BUNDLR_CURRENCY (optional) — currency used, default: 'ar'

Usage example:
    from modules.storage.bundlr import upload_file_to_bundlr
    upload_file_to_bundlr('/tmp/report.pdf')

Note: real upload requires installing Bundlr client or implementing a compatible
upload routine. For now the module raises clear errors if client is missing.
"""
import os
from typing import Dict, Optional

BUNDLR_URL = os.getenv("BUNDLR_URL")
BUNDLR_PRIVATE_KEY = os.getenv("BUNDLR_PRIVATE_KEY")
BUNDLR_CURRENCY = os.getenv("BUNDLR_CURRENCY", "ar")

try:
    # try to import an available Bundlr python client (name may vary)
    # this is optional — many environments will use the node/bundlr-js, not python client
    import bundlr  # type: ignore
    HAS_BUNDLR = True
except Exception:
    HAS_BUNDLR = False


def _upload_via_client(path: str, url: str, private_key: str, currency: str) -> Dict[str, str]:
    """Internal: call actual bundlr client. This is kept separate for easier testing.

    Returns {'tx_id': <id>} on success.
    """
    if not HAS_BUNDLR:
        raise NotImplementedError("Bundlr client is not installed. Install an appropriate bundlr client or implement _upload_via_client.")

    # The exact API depends on the bundlr package. Implementations should adapt
    # here. We provide a minimal example assuming a hypothetical python client.
    # For production, replace with the real client's API calls.
    try:
        client = bundlr.Bundlr(url=url, private_key=private_key, currency=currency)  # type: ignore
        tx = client.upload_file(path)  # pseudo-call — adapt to real client
        return {"tx_id": getattr(tx, "id", None) or str(tx)}
    except Exception as e:
        raise RuntimeError(f"Bundlr client upload failed: {e}")


def upload_file_to_bundlr(path: str, bundlr_url: Optional[str] = None, private_key: Optional[str] = None, currency: Optional[str] = None) -> Dict[str, str]:
    """Upload file to Bundlr. Returns {'tx_id': <id>}.

    If `bundlr_url` or `private_key` are not provided they are read from the
    environment variables `BUNDLR_URL` and `BUNDLR_PRIVATE_KEY` respectively.

    This function intentionally validates configuration and raises intuitive
    errors to help users configure their environment.
    """
    url = bundlr_url or BUNDLR_URL or os.getenv("BUNDLR_URL")
    key = private_key or BUNDLR_PRIVATE_KEY or os.getenv("BUNDLR_PRIVATE_KEY")
    cur = currency or BUNDLR_CURRENCY or os.getenv("BUNDLR_CURRENCY", "ar")

    if not url:
        raise ValueError("Bundlr URL not configured. Set BUNDLR_URL environment variable or pass bundlr_url parameter.")
    if not key:
        raise ValueError("Bundlr private key not configured. Set BUNDLR_PRIVATE_KEY environment variable or pass private_key parameter.")

    # Delegate to client (or internal implementation)
    return _upload_via_client(path, url, key, cur)
