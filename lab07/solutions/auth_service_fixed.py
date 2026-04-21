"""
Lab 7 — Solution: auth_service_fixed.py
========================================
Fixed version of auth_service.py with all 8 OWASP vulnerabilities resolved.
"""

import hashlib
import json
import logging
import os
import sqlite3
import subprocess
from pathlib import Path
from typing import Optional

import bcrypt

DB_PATH = "users.db"
UPLOAD_DIR = "uploads"

logger = logging.getLogger(__name__)


# ── Database setup ───────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            is_active INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()


# ── FIX 1: SQL Injection → Parameterized queries ────────────────────

def login(username: str, password: str) -> Optional[dict]:
    """Authenticate user. Returns user dict or None."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,),
    )
    row = cursor.fetchone()
    conn.close()
    if row and bcrypt.checkpw(password.encode(), row[2].encode()):
        return {"id": row[0], "username": row[1], "email": row[3], "role": row[4]}
    return None


def search_users(search_term: str) -> list[dict]:
    """Search users by username."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, email FROM users WHERE username LIKE ?",
        (f"%{search_term}%",),
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "username": r[1], "email": r[2]} for r in rows]


# ── FIX 2: Insecure Password Storage → bcrypt with salt ─────────────

def register_user(username: str, password: str, email: str) -> dict:
    """Register a new user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (username, hashed, email),
        )
        conn.commit()
        return {"status": "ok", "user_id": cursor.lastrowid}
    except sqlite3.IntegrityError:
        return {"status": "error", "message": "Username already exists"}
    finally:
        conn.close()


# ── FIX 3: Path Traversal → sanitize filename ───────────────────────

def _safe_filepath(filename: str) -> Path:
    """Resolve filename to a safe path within UPLOAD_DIR."""
    upload_dir = Path(UPLOAD_DIR).resolve()
    safe_name = Path(filename).name  # strips directory components
    if not safe_name:
        raise ValueError("Invalid filename")
    resolved = (upload_dir / safe_name).resolve()
    if not str(resolved).startswith(str(upload_dir)):
        raise ValueError("Path traversal detected")
    return resolved


def upload_file(filename: str, content: bytes) -> str:
    """Save uploaded file. Returns the file path."""
    filepath = _safe_filepath(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(content)
    return str(filepath)


def read_file(filename: str) -> Optional[bytes]:
    """Read an uploaded file."""
    try:
        filepath = _safe_filepath(filename)
    except ValueError:
        return None
    if filepath.exists():
        with open(filepath, "rb") as f:
            return f.read()
    return None


# ── FIX 4: Command Injection → no shell=True, list args ─────────────

def get_file_info(filename: str) -> str:
    """Get file metadata using system command."""
    filepath = _safe_filepath(filename)
    result = subprocess.run(
        ["file", str(filepath)],
        capture_output=True,
        text=True,
    )
    return result.stdout


def compress_file(filename: str) -> str:
    """Compress a file using gzip."""
    filepath = _safe_filepath(filename)
    subprocess.run(["gzip", str(filepath)], check=True)
    return f"{filepath}.gz"


# ── FIX 5: Hardcoded Secrets → environment variables ────────────────

def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_api_headers() -> dict:
    api_key = _require_env("API_KEY")
    return {
        "Authorization": f"Bearer {api_key}",
        "X-Api-Key": api_key,
    }


# ── FIX 6: Insecure Deserialization → JSON instead of pickle ────────

def save_session(session_data: dict, filepath: str) -> None:
    """Save session data to file."""
    with open(filepath, "w") as f:
        json.dump(session_data, f)


def load_session(filepath: str) -> dict:
    """Load session data from file."""
    with open(filepath, "r") as f:
        return json.load(f)


# ── FIX 7: Missing Access Control → authorization checks ────────────

def _get_user_role(user_id: int) -> Optional[str]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def get_user_profile(requesting_user_id: int, target_user_id: int) -> Optional[dict]:
    """Get a user's profile. Users can view their own; admins can view any."""
    if requesting_user_id != target_user_id:
        role = _get_user_role(requesting_user_id)
        if role != "admin":
            return None
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, role FROM users WHERE id = ?", (target_user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "email": row[2], "role": row[3]}
    return None


def delete_user(requesting_user_id: int, target_user_id: int) -> bool:
    """Delete a user. Only admins can delete."""
    role = _get_user_role(requesting_user_id)
    if role != "admin":
        return False
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (target_user_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


# ── FIX 8: Information Exposure → generic client message ─────────────

def handle_error(error: Exception) -> dict:
    """Handle errors — log details server-side, return generic message."""
    import traceback
    logger.error("Internal error: %s\n%s", error, traceback.format_exc())
    return {
        "error": "An internal error occurred. Please try again later.",
    }
