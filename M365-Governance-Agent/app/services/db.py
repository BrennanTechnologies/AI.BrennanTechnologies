# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

import json
import sqlite3
from pathlib import Path
from typing import Any

from app.config import Settings


def connect(settings: Settings) -> sqlite3.Connection:
    db_path = Path(settings.db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(settings: Settings) -> None:
    conn = connect(settings)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS action_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_utc TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                action_type TEXT NOT NULL,
                status TEXT NOT NULL,
                is_sensitive INTEGER NOT NULL,
                approved_by TEXT,
                message TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                output_json TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def insert_log(
    settings: Settings,
    *,
    timestamp_utc: str,
    user_id: str,
    role: str,
    action_type: str,
    status: str,
    is_sensitive: bool,
    approved_by: str | None,
    message: str,
    payload: dict[str, Any],
    output: dict[str, Any],
) -> int:
    conn = connect(settings)
    try:
        cursor = conn.execute(
            """
            INSERT INTO action_logs (
                timestamp_utc, user_id, role, action_type, status, is_sensitive,
                approved_by, message, payload_json, output_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp_utc,
                user_id,
                role,
                action_type,
                status,
                1 if is_sensitive else 0,
                approved_by,
                message,
                json.dumps(payload),
                json.dumps(output),
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)
    finally:
        conn.close()


def list_logs(settings: Settings, limit: int = 100) -> list[sqlite3.Row]:
    conn = connect(settings)
    try:
        cursor = conn.execute(
            """
            SELECT id, timestamp_utc, user_id, role, action_type, status, is_sensitive,
                   approved_by, message, payload_json, output_json
            FROM action_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_log(settings: Settings, action_id: int) -> sqlite3.Row | None:
    conn = connect(settings)
    try:
        cursor = conn.execute(
            """
            SELECT id, timestamp_utc, user_id, role, action_type, status, is_sensitive,
                   approved_by, message, payload_json, output_json
            FROM action_logs
            WHERE id = ?
            """,
            (action_id,),
        )
        return cursor.fetchone()
    finally:
        conn.close()


def update_log_status(
    settings: Settings,
    action_id: int,
    *,
    status: str,
    approved_by: str | None,
    message: str,
    output: dict[str, Any],
) -> None:
    conn = connect(settings)
    try:
        conn.execute(
            """
            UPDATE action_logs
            SET status = ?, approved_by = ?, message = ?, output_json = ?
            WHERE id = ?
            """,
            (status, approved_by, message, json.dumps(output), action_id),
        )
        conn.commit()
    finally:
        conn.close()
