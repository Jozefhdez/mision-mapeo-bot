"""
Módulo de base de datos SQLite para cuentas de usuario vinculadas.
"""
import sqlite3
import logging
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class Database:
    """Persiste la vinculación Telegram user → cuenta Bekaab."""

    def __init__(self, db_path: str = "./data/initiatives.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()
        logger.info(f"Database initialized at {db_path}")

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        conn = self._get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_accounts (
                telegram_id INTEGER PRIMARY KEY,
                bekaab_user_id INTEGER NOT NULL,
                bekaab_display_name TEXT,
                bekaab_email TEXT,
                linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def get_user_account(self, telegram_id: int) -> Optional[Dict]:
        conn = self._get_connection()
        row = conn.execute(
            "SELECT * FROM user_accounts WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def save_user_account(self, telegram_id: int, bekaab_user_id: int, display_name: str, email: str):
        conn = self._get_connection()
        conn.execute("""
            INSERT OR REPLACE INTO user_accounts
                (telegram_id, bekaab_user_id, bekaab_display_name, bekaab_email)
            VALUES (?, ?, ?, ?)
        """, (telegram_id, bekaab_user_id, display_name, email))
        conn.commit()
        conn.close()
        logger.info(f"Account linked: telegram {telegram_id} → bekaab {bekaab_user_id}")

    def delete_user_account(self, telegram_id: int):
        conn = self._get_connection()
        conn.execute("DELETE FROM user_accounts WHERE telegram_id = ?", (telegram_id,))
        conn.commit()
        conn.close()
        logger.info(f"Account unlinked for telegram {telegram_id}")
