"""
SQLite helper для хранения результатов расследований:
- Таблица `investigations` (id, address, created_at, notes)
- Таблица `edges` (id, investigation_id, from_addr, to_addr, value, tx_hash, time)

Простой интерфейс: инициализация схемы, добавление расследования, добавление транзакций.
"""
import sqlite3
from typing import Optional, Dict, Any
from datetime import datetime


class ForensicsDB:
    def __init__(self, path: str = "forensics.db"):
        self.path = path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.path)
            self.conn.row_factory = sqlite3.Row

    def init_tables(self) -> None:
        """Создать таблицы, если они не существуют"""
        self.connect()
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS investigations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT NOT NULL,
                created_at TEXT NOT NULL,
                notes TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                investigation_id INTEGER NOT NULL,
                from_addr TEXT,
                to_addr TEXT,
                value TEXT,
                tx_hash TEXT,
                time TEXT,
                FOREIGN KEY (investigation_id) REFERENCES investigations (id) ON DELETE CASCADE
            )
            """
        )
        self.conn.commit()

    def add_investigation(self, address: str, notes: Optional[str] = None) -> int:
        self.connect()
        cur = self.conn.cursor()
        ts = datetime.utcnow().isoformat()
        cur.execute(
            "INSERT INTO investigations (address, created_at, notes) VALUES (?, ?, ?)", (address, ts, notes)
        )
        self.conn.commit()
        return cur.lastrowid

    def add_edge(self, investigation_id: int, from_addr: str, to_addr: str, value: str, tx_hash: str, time: str) -> int:
        self.connect()
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO edges (investigation_id, from_addr, to_addr, value, tx_hash, time) VALUES (?, ?, ?, ?, ?, ?)",
            (investigation_id, from_addr, to_addr, value, tx_hash, time),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_investigation(self, investigation_id: int) -> Dict[str, Any]:
        self.connect()
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM investigations WHERE id = ?", (investigation_id,))
        inv = cur.fetchone()
        if not inv:
            raise KeyError("Investigation not found")
        cur.execute("SELECT * FROM edges WHERE investigation_id = ?", (investigation_id,))
        edges = [dict(r) for r in cur.fetchall()]
        return {"investigation": dict(inv), "edges": edges}

    def list_investigations(self, limit: int = 100, offset: int = 0):
        """Вернуть список расследований (basic pagination)."""
        self.connect()
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM investigations ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset))
        rows = [dict(r) for r in cur.fetchall()]
        return rows

    def delete_investigation(self, investigation_id: int) -> None:
        self.connect()
        cur = self.conn.cursor()
        cur.execute("DELETE FROM investigations WHERE id = ?", (investigation_id,))
        self.conn.commit()

    # Admins table and helpers
    def init_tables(self) -> None:
        """Создать таблицы, если они не существуют"""
        self.connect()
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS investigations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT NOT NULL,
                created_at TEXT NOT NULL,
                notes TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                investigation_id INTEGER NOT NULL,
                from_addr TEXT,
                to_addr TEXT,
                value TEXT,
                tx_hash TEXT,
                time TEXT,
                FOREIGN KEY (investigation_id) REFERENCES investigations (id) ON DELETE CASCADE
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                token TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def add_admin(self, name: str, token: str) -> int:
        """Добавить администратора с токеном (token должен быть уникальным)."""
        self.connect()
        cur = self.conn.cursor()
        ts = datetime.utcnow().isoformat()
        cur.execute(
            "INSERT INTO admins (name, token, created_at) VALUES (?, ?, ?)",
            (name, token, ts),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_admin_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        self.connect()
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM admins WHERE token = ?", (token,))
        r = cur.fetchone()
        return dict(r) if r else None

    def list_admins(self, limit: int = 100, offset: int = 0):
        self.connect()
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM admins ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset))
        rows = [dict(r) for r in cur.fetchall()]
        return rows

    def delete_admin(self, admin_id: int) -> None:
        self.connect()
        cur = self.conn.cursor()
        cur.execute("DELETE FROM admins WHERE id = ?", (admin_id,))
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
