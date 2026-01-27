"""
TraceAnalyzer — простой модуль для анализа истории адреса через Etherscan + Web3.
- Запрашивает транзакции через Etherscan API
- Строит граф адресов (при установленном networkx)
- Экспортирует CSV/построение графа

Примечания безопасности: never commit API keys, используйте .env и конфиг-файлы.
"""
import os
import requests
import csv
from typing import List, Dict, Any
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

ETHERSCAN_API = os.getenv("ETHERSCAN_API_KEY")
ETHERSCAN_BASE = "https://api.etherscan.io/api"

try:
    import networkx as nx
    HAS_NX = True
except Exception:
    HAS_NX = False


class TraceAnalyzer:
    def __init__(self, api_key: str = None):
        # Prefer explicit parameter, then environment variable looked up at runtime.
        # Avoid relying only on the module-level constant so tests can monkeypatch env.
        self.api_key = api_key or os.getenv("ETHERSCAN_API_KEY") or ETHERSCAN_API
        if not self.api_key:
            raise ValueError("Etherscan API key is required. Set ETHERSCAN_API_KEY in .env or pass as parameter.")

    def fetch_txs(self, address: str, page_size: int = 1000) -> List[Dict[str, Any]]:
        """Получить список транзакций для адреса через Etherscan API с постраничной загрузкой.

        Etherscan возвращает данные страницами (page, offset). Метод возвращает полный список.
        """
        all_txs: List[Dict[str, Any]] = []
        page = 1
        while True:
            params = {
                "module": "account",
                "action": "txlist",
                "address": address,
                "startblock": 0,
                "endblock": 99999999,
                "page": page,
                "offset": page_size,
                "sort": "asc",
                "apikey": self.api_key,
            }
            r = requests.get(ETHERSCAN_BASE, params=params, timeout=30)
            if r.status_code != 200:
                raise ConnectionError(f"Etherscan request failed: {r.status_code}")
            j = r.json()
            if j.get("status") != "1":
                # No transactions or error
                break
            batch = j.get("result", [])
            if not batch:
                break
            all_txs.extend(batch)
            if len(batch) < page_size:
                break
            page += 1
        return all_txs

    def analyze_address(self, address: str, build_graph: bool = True) -> Dict[str, Any]:
        txs = self.fetch_txs(address)
        summary = {"address": address, "tx_count": len(txs), "first_tx": None, "last_tx": None}
        if txs:
            summary["first_tx"] = txs[0].get("timeStamp")
            summary["last_tx"] = txs[-1].get("timeStamp")

        edges = []
        for tx in txs:
            edges.append({
                "from": tx.get("from"),
                "to": tx.get("to"),
                "value": tx.get("value"),
                "hash": tx.get("hash"),
                "time": datetime.utcfromtimestamp(int(tx.get("timeStamp"))).isoformat() if tx.get("timeStamp") else None,
            })

        result = {"summary": summary, "edges": edges}

        if build_graph and HAS_NX:
            g = nx.DiGraph()
            for e in edges:
                g.add_node(e["from"])
                g.add_node(e["to"])
                g.add_edge(e["from"], e["to"], value=e["value"], tx=e["hash"], time=e["time"])
            result["graph"] = g

        return result

    def export_edges_csv(self, edges: List[Dict[str, Any]], path: str) -> None:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["from", "to", "value", "hash", "time"])
            writer.writeheader()
            for e in edges:
                writer.writerow(e)

    def analyze_and_store(self, address: str, db, build_graph: bool = False) -> int:
        """Проанализировать адрес и сохранить результаты в базу данных ForensicsDB.

        Возвращает id созданного расследования.
        """
        txs = self.fetch_txs(address)
        edges = []
        for tx in txs:
            edges.append({
                "from": tx.get("from"),
                "to": tx.get("to"),
                "value": tx.get("value"),
                "hash": tx.get("hash"),
                "time": datetime.utcfromtimestamp(int(tx.get("timeStamp"))).isoformat() if tx.get("timeStamp") else None,
            })

        # Создать расследование и сохранить edges
        inv_id = db.add_investigation(address, notes=f"Auto-imported {len(edges)} txs")
        for e in edges:
            db.add_edge(inv_id, e["from"], e["to"], e["value"], e["hash"], e["time"]) 
        return inv_id

