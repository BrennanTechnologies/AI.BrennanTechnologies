# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.config import Settings
from app.models import CoachingSession


def _connect(settings: Settings) -> sqlite3.Connection:
    db_path = Path(settings.db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(settings: Settings) -> None:
    conn = _connect(settings)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS adoption_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_utc TEXT NOT NULL,
                user_id TEXT NOT NULL,
                department TEXT NOT NULL,
                action TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS coaching_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_utc TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                goal TEXT NOT NULL,
                skill_level TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def insert_adoption_event(settings: Settings, user_id: str, department: str, action: str) -> None:
    conn = _connect(settings)
    try:
        conn.execute(
            "INSERT INTO adoption_events (timestamp_utc, user_id, department, action) VALUES (?, ?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), user_id, department, action),
        )
        conn.commit()
    finally:
        conn.close()


def insert_coaching_session(settings: Settings, session: CoachingSession, response_payload: dict) -> None:
    conn = _connect(settings)
    try:
        conn.execute(
            """
            INSERT INTO coaching_sessions (timestamp_utc, user_id, role, goal, skill_level, payload_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session.timestamp_utc.isoformat(),
                session.user_id,
                session.role,
                session.goal,
                session.skill_level,
                json.dumps(response_payload),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_metrics(settings: Settings) -> dict:
    conn = _connect(settings)
    try:
        total_events = conn.execute("SELECT COUNT(*) AS c FROM adoption_events").fetchone()["c"]
        since = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        active_users = conn.execute(
            "SELECT COUNT(DISTINCT user_id) AS c FROM adoption_events WHERE timestamp_utc >= ?",
            (since,),
        ).fetchone()["c"]
        dept_rows = conn.execute(
            """
            SELECT department, COUNT(*) AS count
            FROM adoption_events
            GROUP BY department
            ORDER BY count DESC
            LIMIT 5
            """
        ).fetchall()

        top_departments = [{"department": row["department"], "count": row["count"]} for row in dept_rows]
        return {
            "total_events": int(total_events),
            "active_users_30d": int(active_users),
            "top_departments": top_departments,
        }
    finally:
        conn.close()
