# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from fastapi import Depends, Header, HTTPException, status

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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key.")


def get_user_context(
    _auth: None = Depends(require_api_key),
    x_user_id: str = Header(default="anonymous", alias="X-User-Id"),
    x_role: str = Header(default="viewer", alias="X-Role"),
) -> UserContext:
    normalized = x_role.lower().strip()
    if normalized not in {"viewer", "operator", "admin"}:
        raise HTTPException(status_code=400, detail="X-Role must be viewer, operator, or admin.")
    return UserContext(user_id=x_user_id, role=normalized)  # type: ignore[arg-type]


def require_min_role(current: Role, minimum: Role) -> None:
    ranks = {"viewer": 1, "operator": 2, "admin": 3}
    if ranks[current] < ranks[minimum]:
        raise HTTPException(status_code=403, detail=f"Role {minimum} or higher is required.")
