# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from fastapi import Depends, Header, HTTPException

from app.config import Settings, get_settings


def require_api_key(
    x_api_key: str = Header(default="", alias="X-API-Key"),
    settings: Settings = Depends(get_settings),
) -> None:
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key.")
