"""Простой извлекатель исходников контракта через Etherscan API"""
import os
import requests
from dotenv import load_dotenv
from typing import Optional

load_dotenv()
ETHERSCAN_API = os.getenv("ETHERSCAN_API_KEY")
ETHERSCAN_BASE = "https://api.etherscan.io/api"


def fetch_contract_source(address: str, api_key: Optional[str] = None) -> str:
    """Возвращает исходный код контракта как строку.

    Выбрасывает исключение при ошибке или если исходник отсутствует.
    """
    key = api_key or ETHERSCAN_API
    if not key:
        raise ValueError("Etherscan API key required (set ETHERSCAN_API_KEY in .env or pass as parameter)")

    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": key,
    }
    r = requests.get(ETHERSCAN_BASE, params=params, timeout=20)
    r.raise_for_status()
    j = r.json()
    if j.get("status") != "1":
        raise ValueError(f"Etherscan returned no source for {address}: {j.get('message')}")
    res = j.get("result", [])
    if not res:
        raise ValueError("Empty result from Etherscan")
    src = res[0].get("SourceCode")
    if not src:
        raise ValueError("No SourceCode field for contract")
    # Etherscan may return source code wrapped or flattened — return raw
    return src
