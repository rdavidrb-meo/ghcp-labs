"""
Lab 7 — Solution: test_security.py
====================================
Security regression tests that verify all 8 vulnerabilities are fixed.
Run against the fixed version: auth_service_fixed.py
"""

import json
import os
import sqlite3
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

import bcrypt
import pytest

# Import from the fixed solution
from solutions.auth_service_fixed import (
    DB_PATH,
    UPLOAD_DIR,
    _safe_filepath,
    delete_user,
    get_api_headers,
    get_user_profile,
    handle_error,
    init_db,
    load_session,
    login,
    register_user,
    save_session,
    search_users,
    upload_file,
    read_file,
)


@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    """Use a temporary database and upload dir for each test."""
    db_file = str(tmp_path / "test_users.db")
    upload_dir = str(tmp_path / "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    monkeypatch.setattr("solutions.auth_service_fixed.DB_PATH", db_file)
    monkeypatch.setattr("solutions.auth_service_fixed.UPLOAD_DIR", upload_dir)

    # Initialize DB
    conn = sqlite3.connect(db_file)
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
    # Insert a test user with bcrypt-hashed password
    hashed = bcrypt.hashpw(b"correctpassword", bcrypt.gensalt()).decode()
    conn.execute(
        "INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
        ("testuser", hashed, "test@example.com", "user"),
    )
    # Insert an admin user
    admin_hashed = bcrypt.hashpw(b"adminpass", bcrypt.gensalt()).decode()
    conn.execute(
        "INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
        ("admin", admin_hashed, "admin@example.com", "admin"),
    )
    conn.commit()
    conn.close()

    yield


# ── TEST 1: SQL Injection is fixed ──────────────────────────────────

class TestSQLInjection:
    def test_login_sql_injection_returns_none(self):
        """SQL injection payload should NOT bypass authentication."""
        result = login("' OR '1'='1", "' OR '1'='1")
        assert result is None

    def test_login_sql_injection_union(self):
        result = login("' UNION SELECT 1,2,3,4,5,6--", "anything")
        assert result is None

    def test_login_valid_credentials(self):
        result = login("testuser", "correctpassword")
        assert result is not None
        assert result["username"] == "testuser"

    def test_login_wrong_password(self):
        result = login("testuser", "wrongpassword")
        assert result is None

    def test_search_users_sql_injection(self):
        """SQL injection in search should not leak data."""
        results = search_users("' OR '1'='1")
        # Should return empty or only legitimate matches, not all users
        for user in results:
            assert "' OR '1'='1" in user["username"] or results == []


# ── TEST 2: Password hashing is secure ──────────────────────────────

class TestPasswordStorage:
    def test_password_not_stored_as_md5(self, tmp_path, monkeypatch):
        """Passwords should be hashed with bcrypt, not MD5."""
        import hashlib
        register_user("newuser", "mypassword", "new@example.com")

        db_file = str(tmp_path / "test_users.db")
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = 'newuser'")
        stored_hash = cursor.fetchone()[0]
        conn.close()

        # Should NOT be an MD5 hash
        md5_hash = hashlib.md5(b"mypassword").hexdigest()
        assert stored_hash != md5_hash

        # Should be a valid bcrypt hash (starts with $2b$)
        assert stored_hash.startswith("$2b$")

    def test_bcrypt_verify_works(self):
        """Registered user should be able to log in."""
        register_user("bcryptuser", "securepass", "bcrypt@example.com")
        result = login("bcryptuser", "securepass")
        assert result is not None
        assert result["username"] == "bcryptuser"


# ── TEST 3: Path traversal is blocked ───────────────────────────────

class TestPathTraversal:
    def test_upload_path_traversal_blocked(self):
        """Attempting path traversal should strip directory components."""
        result = upload_file("../../etc/passwd", b"malicious")
        assert "etc" not in result or Path(result).parent.name != "etc"
        # File should be stored in UPLOAD_DIR with name "passwd"
        assert Path(result).name == "passwd"

    def test_read_path_traversal_blocked(self):
        """Reading ../../etc/passwd should not work."""
        result = read_file("../../etc/passwd")
        assert result is None

    def test_safe_filepath_rejects_traversal(self):
        """_safe_filepath should strip directory components."""
        result = _safe_filepath("../../../etc/passwd")
        assert result.name == "passwd"

    def test_empty_filename_rejected(self):
        with pytest.raises(ValueError, match="Invalid filename"):
            _safe_filepath("")


# ── TEST 4: Command injection is blocked ─────────────────────────────

class TestCommandInjection:
    def test_get_file_info_no_shell_injection(self, tmp_path):
        """Semicolons in filename should not execute commands."""
        # Create a safe test file
        upload_dir = tmp_path / "uploads"
        test_file = upload_dir / "safe.txt"
        test_file.write_text("test")
        # This should not execute 'rm -rf /'
        # The _safe_filepath will sanitize the name
        with pytest.raises((ValueError, subprocess.CalledProcessError, FileNotFoundError)):
            from solutions.auth_service_fixed import get_file_info
            get_file_info("; rm -rf /")

    def test_compress_file_no_injection(self):
        """Command injection via filename should be prevented."""
        with pytest.raises((ValueError, subprocess.CalledProcessError, FileNotFoundError)):
            from solutions.auth_service_fixed import compress_file
            compress_file("; cat /etc/passwd")


# ── TEST 5: No hardcoded secrets ─────────────────────────────────────

class TestHardcodedSecrets:
    def test_api_headers_use_env_var(self, monkeypatch):
        """API key should come from environment, not hardcoded."""
        monkeypatch.setenv("API_KEY", "test-key-from-env")
        headers = get_api_headers()
        assert headers["Authorization"] == "Bearer test-key-from-env"
        assert headers["X-Api-Key"] == "test-key-from-env"

    def test_missing_env_var_raises(self, monkeypatch):
        """Missing env vars should raise, not fall back to hardcoded."""
        monkeypatch.delenv("API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="Missing required environment variable"):
            get_api_headers()


# ── TEST 6: No insecure deserialization ──────────────────────────────

class TestDeserialization:
    def test_session_uses_json_not_pickle(self, tmp_path):
        """Session should be saved as JSON, not pickle."""
        session_file = str(tmp_path / "session.json")
        data = {"user_id": 1, "role": "user"}
        save_session(data, session_file)

        # File should be valid JSON
        with open(session_file, "r") as f:
            loaded = json.load(f)
        assert loaded == data

    def test_load_session_returns_dict(self, tmp_path):
        session_file = str(tmp_path / "session.json")
        data = {"user_id": 42, "token": "abc"}
        save_session(data, session_file)
        loaded = load_session(session_file)
        assert loaded == data


# ── TEST 7: Access control enforced ──────────────────────────────────

class TestAccessControl:
    def test_user_can_view_own_profile(self):
        result = get_user_profile(1, 1)
        assert result is not None
        assert result["username"] == "testuser"

    def test_user_cannot_view_other_profile(self):
        """Non-admin user should NOT see another user's profile."""
        result = get_user_profile(1, 2)  # user 1 (non-admin) trying to view user 2
        assert result is None

    def test_admin_can_view_any_profile(self):
        result = get_user_profile(2, 1)  # user 2 (admin) viewing user 1
        assert result is not None
        assert result["username"] == "testuser"

    def test_non_admin_cannot_delete_user(self):
        """Regular user should NOT be able to delete another user."""
        result = delete_user(1, 2)  # user 1 (non-admin) trying to delete user 2
        assert result is False

    def test_admin_can_delete_user(self):
        """Admin should be able to delete a user."""
        # Register a disposable user
        register_user("disposable", "pass123", "del@example.com")
        # Find their ID
        import solutions.auth_service_fixed as mod
        conn = sqlite3.connect(mod.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = 'disposable'")
        user_id = cursor.fetchone()[0]
        conn.close()

        result = delete_user(2, user_id)  # user 2 is admin
        assert result is True


# ── TEST 8: Error handling doesn't leak info ─────────────────────────

class TestInformationExposure:
    def test_error_response_is_generic(self):
        """Error response should NOT contain traceback or internal paths."""
        result = handle_error(ValueError("test error"))
        assert "traceback" not in result
        assert "db_path" not in result
        assert "server_os" not in result
        assert "python_path" not in result
        assert "error" in result

    def test_error_does_not_leak_exception_details(self):
        result = handle_error(RuntimeError("secret database connection string"))
        assert "secret database connection string" not in result["error"]
