# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from datetime import datetime, timezone
from pathlib import Path

from app.models import AuditRecord

AUDIT_LOG_PATH = Path("data/audit.log")


def log_event(run_id: str, user_id: str, role: str, action: str, status: str, detail: str) -> None:
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = (
        f"{datetime.now(timezone.utc).isoformat()}|run={run_id}|user={user_id}|role={role}|"
        f"action={action}|status={status}|detail={detail}"
    )
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def read_audit(limit: int = 100) -> list[AuditRecord]:
    if not AUDIT_LOG_PATH.exists():
        return []

    lines = AUDIT_LOG_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
    selected = lines[-limit:]
    rows: list[AuditRecord] = []

    for line in reversed(selected):
        parts = line.split("|")
        if len(parts) < 7:
            continue
        rows.append(
            AuditRecord(
                run_id=parts[1].split("=", 1)[1],
                timestamp_utc=datetime.fromisoformat(parts[0]),
                user_id=parts[2].split("=", 1)[1],
                role=parts[3].split("=", 1)[1],
                action=parts[4].split("=", 1)[1],
                status=parts[5].split("=", 1)[1],
                detail=parts[6].split("=", 1)[1],
            )
        )
    return rows
