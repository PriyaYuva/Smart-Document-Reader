
# database.py
import sqlite3
import json
import os

DB_PATH = "documents.db"

def init_db():
    """Initialize the SQLite database and create the docs table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fileName TEXT,
            text TEXT,
            extracted JSON,
            meta JSON
        )
        """
    )
    conn.commit()
    conn.close()


def save_document(file_name, text, extracted, meta):
    """Save a processed document into the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO docs (fileName, text, extracted, meta) VALUES (?, ?, ?, ?)",
        (file_name, text, json.dumps(extracted), json.dumps(meta)),
    )
    conn.commit()
    doc_id = c.lastrowid
    conn.close()
    return doc_id
