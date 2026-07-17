# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from fastapi import Depends, Header, HTTPException

from app.config import Settings, get_settings
from app.models import Role


class UserContext:
    def __init__(self, user_id: str, role: Role):
        self.user_id = user_id
        self.role = role


def require_api_key(
    x_api_key: str = Header(default="", alias="X-API-Key"),
    settings: Settings = Depends(get_settings),
) -> None:
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key.")


def get_user_context(
    _: None = Depends(require_api_key),
    x_user_id: str = Header(default="anonymous", alias="X-User-Id"),
    x_role: str = Header(default="viewer", alias="X-Role"),
) -> UserContext:
    role = x_role.lower().strip()
    if role not in {"viewer", "operator", "admin"}:
        raise HTTPException(status_code=400, detail="X-Role must be viewer, operator, or admin.")
    return UserContext(x_user_id, role)  # type: ignore[arg-type]


def ensure_min_role(current: Role, minimum: Role) -> None:
    rank = {"viewer": 1, "operator": 2, "admin": 3}
    if rank[current] < rank[minimum]:
        raise HTTPException(status_code=403, detail=f"{minimum} role required.")
