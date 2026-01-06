from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str


class UserRead(BaseModel):
    id: UUID
    username: str


class TokenResponse(BaseModel):
    token: str
# Placeholder for Phase II schemas (User, Todo changes)
