# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from datetime import datetime, timezone
from pathlib import Path

from app.models import AuditRecord

LOG_FILE = Path("data/workflow_audit.log")


def write_audit(run_id: str, user_id: str, role: str, event: str, status: str, detail: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    line = (
        f"{datetime.now(timezone.utc).isoformat()}|run_id={run_id}|user_id={user_id}|"
        f"role={role}|event={event}|status={status}|detail={detail}"
    )
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(line + "\n")


def read_audit(limit: int = 100) -> list[AuditRecord]:
    if not LOG_FILE.exists():
        return []

    entries = LOG_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()[-limit:]
    records: list[AuditRecord] = []

    for entry in reversed(entries):
        parts = entry.split("|")
        if len(parts) < 7:
            continue
        records.append(
            AuditRecord(
                timestamp_utc=datetime.fromisoformat(parts[0]),
                run_id=parts[1].split("=", 1)[1],
                user_id=parts[2].split("=", 1)[1],
                role=parts[3].split("=", 1)[1],
                event=parts[4].split("=", 1)[1],
                status=parts[5].split("=", 1)[1],
                detail=parts[6].split("=", 1)[1],
            )
        )
    return records
