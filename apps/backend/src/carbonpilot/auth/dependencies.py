from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from carbonpilot.auth.security import TokenPayload, decode_access_token

security_scheme = HTTPBearer(auto_error=True)


class AuthenticatedUser(BaseModel):
    user_id: str
    organization_id: str
    facility_id: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> AuthenticatedUser:
    token = credentials.credentials
    try:
        payload: TokenPayload = decode_access_token(token)
        return AuthenticatedUser(
            user_id=payload.sub,
            organization_id=payload.organization_id,
            facility_id=payload.facility_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc