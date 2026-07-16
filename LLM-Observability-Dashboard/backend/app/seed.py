# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from datetime import UTC, datetime, timedelta
from random import Random

from sqlalchemy.orm import Session

from app.models import LLMEvent


def seed_events(db: Session, count: int = 240) -> int:
    existing = db.query(LLMEvent).count()
    if existing > 0:
        return 0

    rng = Random(7)
    now = datetime.now(UTC).replace(tzinfo=None)
    models = ["gpt-4.1-mini", "gpt-4.1", "claude-3.5-sonnet", "gemini-2.5-flash"]
    providers = ["openai", "anthropic", "google"]

    rows: list[LLMEvent] = []
    for i in range(count):
        timestamp = now - timedelta(minutes=(count - i) * 2)
        status = "success" if rng.random() > 0.14 else "error"
        prompt_tokens = rng.randint(100, 1400)
        completion_tokens = rng.randint(40, 900)
        total_tokens = prompt_tokens + completion_tokens
        latency_ms = rng.randint(220, 2400)
        cost_usd = round(total_tokens * rng.uniform(0.000002, 0.000018), 5)

        rows.append(
            LLMEvent(
                timestamp=timestamp,
                request_id=f"seed_req_{i}",
                model=rng.choice(models),
                provider=rng.choice(providers),
                status=status,
                latency_ms=latency_ms,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost_usd=cost_usd,
                input="User prompt text",
                output="Model output text",
                extra_metadata={"env": "dev", "seed": True},
            )
        )

    db.bulk_save_objects(rows)
    db.commit()
    return len(rows)
