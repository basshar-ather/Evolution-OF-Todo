from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, status

from .database import init_db, get_session
from .models import TodoCreate, TodoRead
from . import crud
from .schemas import UserCreate, TokenResponse
from .utils import generate_token
from .auth import get_current_user
from fastapi import Depends
from .chat import handle_chat

app = FastAPI(title="Evolution of Todo - Phase I")


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/todos", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(todo_in: TodoCreate, current_user=Depends(get_current_user)):
    if not todo_in.title or not todo_in.title.strip():
        raise HTTPException(status_code=400, detail="title is required")
    with get_session() as session:
        todo = crud.create_todo(session, todo_in, owner=current_user)
        return todo


@app.get("/todos", response_model=List[TodoRead])
def list_todos(completed: Optional[bool] = None, sort: Optional[str] = None, current_user: Optional[object] = Depends(lambda: None)):
    # `current_user` dependency is optional; when provided, only return user's todos.
    with get_session() as session:
        owner = None
        if current_user:
            owner = current_user
        return crud.list_todos(session, owner=owner, completed=completed, sort_by=sort)


@app.put("/todos/{todo_id}", response_model=TodoRead)
def update_todo(todo_id: UUID, todo_in: TodoCreate, current_user=Depends(get_current_user)):
    if not todo_in.title or not todo_in.title.strip():
        raise HTTPException(status_code=400, detail="title is required")
    with get_session() as session:
        todo = crud.get_todo(session, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        if todo.owner_id and todo.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return crud.update_todo(session, todo, todo_in)


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: UUID, current_user=Depends(get_current_user)):
    with get_session() as session:
        todo = crud.get_todo(session, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        if todo.owner_id and todo.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        crud.delete_todo(session, todo)
        return


@app.post("/users", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate):
    if not user_in.username or not user_in.username.strip():
        raise HTTPException(status_code=400, detail="username is required")
    token = generate_token(16)
    with get_session() as session:
        # create user and return token
        user = crud.create_user(session, username=user_in.username, token=token)
        return {"token": user.token}


@app.post("/chat")
def chat_endpoint(payload: dict, current_user=Depends(lambda: None)):
    message = payload.get("message") if isinstance(payload, dict) else None
    if not message:
        raise HTTPException(status_code=400, detail="message is required")
    result = handle_chat(message, user=current_user)
    return result
