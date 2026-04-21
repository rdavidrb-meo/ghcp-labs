"""
Lab 5 — Refactoring & Migration
=================================
A Flask-based REST API for a task manager, written in an older style.
Participants use Copilot to refactor it and optionally migrate to FastAPI.
"""

from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = os.getenv("DB_PATH", "tasks.db")


# ── Database setup (no ORM, raw SQL) ────────────────────────────────

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            priority INTEGER DEFAULT 0,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()
    conn.close()


# ── Routes (intentionally verbose and repetitive) ───────────────────

@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    status_filter = request.args.get("status")
    if status_filter:
        cursor.execute("SELECT * FROM tasks WHERE status = ?", (status_filter,))
    else:
        cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    tasks = []
    for row in rows:
        tasks.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "status": row[3],
            "priority": row[4],
            "created_at": row[5],
            "updated_at": row[6],
        })
    return jsonify(tasks)


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Task not found"}), 404
    task = {
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "status": row[3],
        "priority": row[4],
        "created_at": row[5],
        "updated_at": row[6],
    }
    return jsonify(task)


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "title is required"}), 400
    title = data["title"]
    description = data.get("description", "")
    priority = data.get("priority", 0)
    now = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description, status, priority, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (title, description, "pending", priority, now, now),
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": task_id, "title": title, "status": "pending"}), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404
    title = data.get("title", row[1])
    description = data.get("description", row[2])
    status = data.get("status", row[3])
    priority = data.get("priority", row[4])
    now = datetime.now().isoformat()
    cursor.execute(
        "UPDATE tasks SET title=?, description=?, status=?, priority=?, updated_at=? WHERE id=?",
        (title, description, status, priority, now, task_id),
    )
    conn.commit()
    conn.close()
    return jsonify({"id": task_id, "title": title, "status": status})


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Task deleted"}), 200


@app.route("/tasks/stats", methods=["GET"])
def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
    pending = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed'")
    completed = cursor.fetchone()[0]
    cursor.execute("SELECT AVG(priority) FROM tasks")
    avg_priority = cursor.fetchone()[0] or 0
    conn.close()
    return jsonify({
        "total": total,
        "pending": pending,
        "completed": completed,
        "avg_priority": round(avg_priority, 2),
    })


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
