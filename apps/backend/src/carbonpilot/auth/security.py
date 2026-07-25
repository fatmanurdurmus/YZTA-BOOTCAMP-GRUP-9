from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
from pydantic import BaseModel, Field

from carbonpilot.config import get_settings


class TokenPayload(BaseModel):
    sub: str = Field(..., description="User ID")
    organization_id: str = Field(..., description="Organization ID")
    facility_id: str = Field(..., description="Facility ID")
    exp: int = Field(..., description="Expiration timestamp")


class TokenRequest(BaseModel):
    user_id: str = Field(..., example="usr_123456")
    organization_id: str = Field(..., example="org_acme_corp")
    facility_id: str = Field(..., example="fac_furnace_a")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int


def create_access_token(
    user_id: str,
    organization_id: str,
    facility_id: str,
    expires_delta: timedelta | None = None,
) -> str:
    settings = get_settings()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)

    to_encode: Dict[str, Any] = {
        "sub": user_id,
        "organization_id": organization_id,
        "facility_id": facility_id,
        "exp": int(expire.timestamp()),
    }
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> TokenPayload:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return TokenPayload(**payload)
    except jwt.PyJWTError as exc:
        raise ValueError("Invalid or expired authentication token") from exc