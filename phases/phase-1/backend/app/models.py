from typing import Optional
from datetime import datetime
from uuid import uuid4, UUID
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship


class Status(str, Enum):
    pending = "pending"
    completed = "completed"


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    username: str = Field(index=True, unique=True)
    token: str = Field(default_factory=lambda: uuid4().hex, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TodoBase(SQLModel):
    title: str
    description: Optional[str] = None
    status: Status = Field(default=Status.pending)
    priority: int = Field(default=0)
    due_date: Optional[datetime] = None


class Todo(TodoBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    owner_id: Optional[UUID] = Field(default=None, foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TodoCreate(TodoBase):
    pass


class TodoRead(TodoBase):
    id: UUID
    owner_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
