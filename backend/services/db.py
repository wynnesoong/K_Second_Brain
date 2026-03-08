import sqlite3
import os
from typing import Dict, Any, Optional

DB_PATH = "data/second_brain.db"

class Database:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        # Create Settings Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        # Create FTS Table for Notes (as per architecture)
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
                title,
                content,
                path UNINDEXED
            )
        ''')
        self.conn.commit()

    def get_setting(self, key: str) -> Optional[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM system_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row['value'] if row else None

    def get_all_settings(self) -> Dict[str, str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT key, value FROM system_settings")
        return {row['key']: row['value'] for row in cursor.fetchall()}

    def set_setting(self, key: str, value: str):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO system_settings (key, value) 
            VALUES (?, ?) 
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        ''', (key, value))
        self.conn.commit()

    def close(self):
        self.conn.close()

# Global DB Instance
db = Database()
