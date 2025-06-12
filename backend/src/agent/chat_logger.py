# src/utils/chat_logger.py

import sqlite3
from datetime import datetime

DB_FILE = "chat_logs.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS chat_sessions (
        id TEXT PRIMARY KEY,
        created_at TEXT,
        entity TEXT
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        session_id TEXT,
        role TEXT,
        content TEXT,
        timestamp TEXT
    )""")
    conn.commit()
    conn.close()

def log_session(session_id: str, entity: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    INSERT OR IGNORE INTO chat_sessions (id, created_at, entity)
    VALUES (?, ?, ?)
    """, (session_id, datetime.now().isoformat(), entity))
    conn.commit()
    conn.close()

def log_message(session_id: str, role: str, content: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    INSERT INTO chat_messages (session_id, role, content, timestamp)
    VALUES (?, ?, ?, ?)
    """, (session_id, role, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_chat_history(session_id: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    SELECT role, content FROM chat_messages
    WHERE session_id = ? ORDER BY timestamp ASC
    """, (session_id,))
    rows = c.fetchall()
    conn.close()
    return [{"role": role, "content": content} for role, content in rows]
