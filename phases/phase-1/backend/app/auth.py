from fastapi import Depends, HTTPException, status, Header
from typing import Optional

from .database import get_session
from .crud import get_user_by_token


def get_current_user(authorization: Optional[str] = Header(None)):
    # Expect header: Authorization: Token <token>
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "token":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header format")
    token = parts[1]
    with get_session() as session:
        user = get_user_by_token(session, token)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user
# Optional current user dependency: returns `None` when no header provided,
# otherwise validates the token and returns the user (or raises 401).
def optional_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "token":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header format")
    token = parts[1]
    with get_session() as session:
        user = get_user_by_token(session, token)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user
# Placeholder for Phase II auth (to be implemented)
