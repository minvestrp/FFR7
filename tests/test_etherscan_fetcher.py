import os
import pytest
from modules.extractors.etherscan_fetcher import fetch_contract_source


def test_fetch_requires_api_key(monkeypatch):
    # Temporarily ensure ENV has no key
    monkeypatch.delenv('ETHERSCAN_API_KEY', raising=False)
    with pytest.raises(ValueError):
        fetch_contract_source('0x1111111111111111111111111111111111111111')
