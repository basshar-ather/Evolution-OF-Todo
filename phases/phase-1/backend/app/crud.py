from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlmodel import Session, select

from .models import Todo, TodoCreate, User


def create_todo(session: Session, todo_in: TodoCreate, owner: Optional[User] = None) -> Todo:
	data = todo_in.dict()
	if owner:
		data["owner_id"] = owner.id
	todo = Todo(**data)
	session.add(todo)
	session.commit()
	session.refresh(todo)
	return todo


def list_todos(session: Session, owner: Optional[User] = None, completed: Optional[bool] = None, sort_by: Optional[str] = None) -> List[Todo]:
	q = select(Todo)
	if owner:
		q = q.where(Todo.owner_id == owner.id)
	if completed is not None:
		from .models import Status
		if completed:
			q = q.where(Todo.status == Status.completed)
		else:
			q = q.where(Todo.status == Status.pending)
	if sort_by:
		# support 'due_date' or '-due_date' for descending
		if sort_by == "due_date":
			q = q.order_by(Todo.due_date)
		elif sort_by == "-due_date":
			q = q.order_by(Todo.due_date.desc())
	return session.exec(q).all()


def get_todo(session: Session, todo_id: UUID) -> Optional[Todo]:
	return session.get(Todo, todo_id)


def update_todo(session: Session, todo: Todo, todo_in: TodoCreate) -> Todo:
	todo.title = todo_in.title
	todo.description = todo_in.description
	todo.status = todo_in.status
	todo.priority = todo_in.priority
	todo.due_date = todo_in.due_date
	todo.updated_at = datetime.utcnow()
	session.add(todo)
	session.commit()
	session.refresh(todo)
	return todo


def delete_todo(session: Session, todo: Todo) -> None:
	session.delete(todo)
	session.commit()


def create_user(session: Session, username: str, token: str) -> User:
	user = User(username=username, token=token)
	session.add(user)
	session.commit()
	session.refresh(user)
	return user


def get_user_by_token(session: Session, token: str) -> Optional[User]:
	return session.exec(select(User).where(User.token == token)).first()


