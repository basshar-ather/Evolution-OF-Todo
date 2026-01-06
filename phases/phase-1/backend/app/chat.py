from typing import Optional, Dict, Any
import re
from .crud import create_todo, list_todos, get_todo, update_todo, delete_todo
from .database import get_session
from .models import TodoCreate, User


def parse_message(message: str) -> Dict[str, Any]:
    m = message.strip()
    # create: "add todo Buy milk"
    if m.lower().startswith("add todo") or m.lower().startswith("create todo"):
        # extract title after keyword
        title = m.split(None, 2)[2] if len(m.split(None, 2)) >= 3 else ""
        return {"intent": "create", "title": title}

    # list: "list todos" or "show todos"
    if m.lower().startswith("list todos") or m.lower().startswith("show todos"):
        return {"intent": "list"}

    # delete: "delete todo <id>"
    dm = re.match(r"(?:delete|remove) todo\s+([0-9a-fA-F-]+)", m, re.I)
    if dm:
        return {"intent": "delete", "id": dm.group(1)}

    # update: "update todo <id> title Buy bread"
    um = re.match(r"update todo\s+([0-9a-fA-F-]+)\s+title\s+(.+)", m, re.I)
    if um:
        return {"intent": "update", "id": um.group(1), "title": um.group(2)}

    return {"intent": "unknown"}


def handle_chat(message: str, user: Optional[User] = None) -> Dict[str, Any]:
    parsed = parse_message(message)
    intent = parsed.get("intent")
    with get_session() as session:
        if intent == "create":
            title = parsed.get("title") or "Untitled"
            todo_in = TodoCreate(title=title)
            todo = create_todo(session, todo_in, owner=user)
            return {"result": "created", "todo": todo.dict()}

        if intent == "list":
            todos = list_todos(session, owner=user)
            return {"result": "list", "todos": [t.dict() for t in todos]}

        if intent == "delete":
            tid = parsed.get("id")
            todo = get_todo(session, tid)
            if not todo:
                return {"result": "not_found"}
            if todo.owner_id and user and todo.owner_id != user.id:
                return {"result": "forbidden"}
            delete_todo(session, todo)
            return {"result": "deleted", "id": tid}

        if intent == "update":
            tid = parsed.get("id")
            todo = get_todo(session, tid)
            if not todo:
                return {"result": "not_found"}
            if todo.owner_id and user and todo.owner_id != user.id:
                return {"result": "forbidden"}
            # only support title updates via chat for now
            todo_in = TodoCreate(title=parsed.get("title"), description=todo.description or None)
            updated = update_todo(session, todo, todo_in)
            return {"result": "updated", "todo": updated.dict()}

        return {"result": "unknown_command"}
# Placeholder for chat integration (Phase III)
