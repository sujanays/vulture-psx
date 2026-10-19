import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

DB_PATH = os.getenv("VULTURE_DB_PATH", "/app/vulture.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                status TEXT NOT NULL,
                score INTEGER DEFAULT 0,
                grade TEXT DEFAULT 'F',
                result_json TEXT,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_task_id ON scans(task_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON scans(created_at DESC)")
        conn.commit()

def create_scan(task_id: str, url: str) -> Dict:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO scans (task_id, url, status) VALUES (?, ?, ?)",
            (task_id, url, "PENDING")
        )
        conn.commit()
    return {"task_id": task_id, "url": url, "status": "PENDING"}

def update_scan_status(
    task_id: str,
    status: str,
    score: Optional[int] = None,
    grade: Optional[str] = None,
    result_json: Optional[Dict] = None,
    error: Optional[str] = None
):
    with get_connection() as conn:
        now = datetime.utcnow().isoformat() if status in ("SUCCESS", "FAILURE") else None
        res_str = json.dumps(result_json) if result_json is not None else None
        conn.execute(
            """
            UPDATE scans
            SET status = ?,
                score = COALESCE(?, score),
                grade = COALESCE(?, grade),
                result_json = COALESCE(?, result_json),
                error = COALESCE(?, error),
                completed_at = COALESCE(?, completed_at)
            WHERE task_id = ?
            """,
            (status, score, grade, res_str, error, now, task_id)
        )
        conn.commit()

def get_scan(task_id: str) -> Optional[Dict]:
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM scans WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        if res.get("result_json"):
            try:
                res["result"] = json.loads(res["result_json"])
            except Exception:
                res["result"] = None
        else:
            res["result"] = None
        return res

def list_scans(limit: int = 50) -> List[Dict]:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, task_id, url, status, score, grade, result_json, error, created_at, completed_at FROM scans ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        result = []
        for r in rows:
            item = dict(r)
            if item.get("result_json"):
                try:
                    item["result"] = json.loads(item["result_json"])
                except Exception:
                    item["result"] = None
            else:
                item["result"] = None
            result.append(item)
        return result

def delete_scan(task_id: str) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM scans WHERE task_id = ?", (task_id,))
        conn.commit()
        return cursor.rowcount > 0
