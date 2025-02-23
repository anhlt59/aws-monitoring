from typing import Annotated

from fastapi import Header

from app.common.configs import API_KEY
from app.common.exceptions.http import UnauthorizedException


async def api_key_required(x_api_key: Annotated[str | None, Header()] = None):
    if x_api_key is None:
        raise UnauthorizedException("API Key is required")
    if x_api_key != API_KEY:
        raise UnauthorizedException("Invalid API Key")
