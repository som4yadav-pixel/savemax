from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Iterable

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
USERS_DB = DATA_DIR / "savemax_users.db"
HISTORY_DB = DATA_DIR / "savemax_history.db"

SCHEMA_USERS = """
CREATE TABLE IF NOT EXISTS users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT UNIQUE NOT NULL,
	password_hash BLOB NOT NULL,
	created_at TEXT NOT NULL
);
"""

SCHEMA_HISTORY = """
CREATE TABLE IF NOT EXISTS history (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT NOT NULL,
	regime TEXT NOT NULL,
	income REAL NOT NULL,
	deductions_old REAL NOT NULL,
	tax REAL NOT NULL,
	created_at TEXT NOT NULL
);
"""

SCHEMA_HISTORY_INDEX = """
CREATE INDEX IF NOT EXISTS idx_history_user ON history(username, created_at DESC);
"""

def ensure_dbs() -> None:
	DATA_DIR.mkdir(parents=True, exist_ok=True)
	with sqlite3.connect(USERS_DB) as con:
		con.execute(SCHEMA_USERS)
		con.commit()
	with sqlite3.connect(HISTORY_DB) as con:
		con.execute(SCHEMA_HISTORY)
		con.execute(SCHEMA_HISTORY_INDEX)
		con.commit()


@contextmanager

def connect(path: Path):
	con = sqlite3.connect(path)
	try:
		yield con
	finally:
		con.close()


def create_user(username: str, password_hash: bytes) -> bool:
	ensure_dbs()
	with connect(USERS_DB) as con:
		try:
			con.execute(
				"INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
				(username, password_hash, datetime.utcnow().isoformat()),
			)
			con.commit()
			return True
		except sqlite3.IntegrityError:
			return False


def get_user_hash(username: str) -> Optional[bytes]:
	ensure_dbs()
	with connect(USERS_DB) as con:
		cur = con.execute("SELECT password_hash FROM users WHERE username=?", (username,))
		row = cur.fetchone()
		return row[0] if row else None


def save_history(username: str, regime: str, income: float, deductions_old: float, tax: float) -> None:
	ensure_dbs()
	with connect(HISTORY_DB) as con:
		con.execute(
			"INSERT INTO history (username, regime, income, deductions_old, tax, created_at) VALUES (?, ?, ?, ?, ?, ?)",
			(username, regime, income, deductions_old, tax, datetime.utcnow().isoformat()),
		)
		con.commit()


def get_recent_history(username: str, limit: int = 10) -> List[Tuple]:
	ensure_dbs()
	with connect(HISTORY_DB) as con:
		cur = con.execute(
			"SELECT created_at, regime, income, tax FROM history WHERE username=? ORDER BY created_at DESC LIMIT ?",
			(username, limit),
		)
		return cur.fetchall() 