"""Arweave uploader stub. Real upload requires wallet/key and a proper implementation.

This module provides a clear API and a configurable hook for later full implementation.
"""
import os
from typing import Dict

ARWEAVE_KEY = os.getenv("ARWEAVE_KEY")


def upload_file_to_arweave(path: str) -> Dict[str, str]:
    """Upload a file to Arweave or via Bundlr fallback.

    Behavior:
    - If `ARWEAVE_KEY` is set and a direct Arweave uploader is implemented, use it (not implemented here).
    - Otherwise, if Bundlr configuration (`BUNDLR_URL` and `BUNDLR_PRIVATE_KEY`) is present, delegate to Bundlr.

    Returns a dict with at least {'tx_id': <id>} on success.
    """
    # If direct Arweave is configured in future, implement here.
    if ARWEAVE_KEY:
        raise NotImplementedError("Direct Arweave upload configured, but direct uploader not implemented. Consider using Bundlr or implement Arweave client.")

    # Try Bundlr as a convenient relayer if available
    try:
        from .bundlr import upload_file_to_bundlr, BUNDLR_URL, BUNDLR_PRIVATE_KEY
    except Exception:
        raise NotImplementedError("Arweave upload is not configured. Set ARWEAVE_KEY or configure Bundlr (BUNDLR_URL & BUNDLR_PRIVATE_KEY).")

    if not (BUNDLR_URL and BUNDLR_PRIVATE_KEY):
        raise NotImplementedError("Bundlr is not configured (BUNDLR_URL / BUNDLR_PRIVATE_KEY).")

    return upload_file_to_bundlr(path)
