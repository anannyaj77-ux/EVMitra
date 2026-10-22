"""
EVMitra Database Helper
Handles all SQLite database connections and operations
"""

import sqlite3
import os

# Database file path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "evmitra.db")


def get_connection():
    """Get a SQLite database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def execute_query(query, params=()):
    """Execute a SELECT query and return all rows as a list of dicts."""
    conn = get_connection()
    try:
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def execute_write(query, params=()):
    """Execute an INSERT/UPDATE/DELETE and return the last row id."""
    conn = get_connection()
    try:
        cursor = conn.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def execute_many(query, data):
    """Execute a batch INSERT/UPDATE for multiple rows."""
    conn = get_connection()
    try:
        conn.executemany(query, data)
        conn.commit()
    finally:
        conn.close()
