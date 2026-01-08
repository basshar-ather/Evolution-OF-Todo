"""Simple in-memory console for the Todo backend.

Run with the workspace Python virtualenv from the repo root:

    python scripts/console_app.py

This imports the app's DB helpers and performs CRUD directly in-process.
"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "phases" / "phase-1" / "backend"
sys.path.insert(0, str(BACKEND))

from app.database import init_db, get_session
from app import crud
from app.models import TodoCreate

def repl():
    init_db()
    print("Todo console (type 'help')")
    while True:
        try:
            cmd = input('> ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nbye')
            return
        if not cmd:
            continue
        if cmd in ('q','quit','exit'):
            print('bye')
            return
        if cmd == 'help':
            print('commands: list, create <title>|<desc>, delete <id>, update <id>|<title>|<desc>')
            continue
        if cmd == 'list':
            with get_session() as s:
                todos = crud.list_todos(s)
                for t in todos:
                    print(f"{t.id} {t.title} [{t.status}] - {t.description}")
            continue
        if cmd.startswith('create '):
            rest = cmd[len('create '):]
            parts = rest.split('|',1)
            title = parts[0].strip()
            desc = parts[1].strip() if len(parts)>1 else ''
            with get_session() as s:
                todo = crud.create_todo(s, TodoCreate(title=title, description=desc))
                print('created', todo.id)
            continue
        if cmd.startswith('delete '):
            tid = cmd.split()[1]
            with get_session() as s:
                t = crud.get_todo(s, tid)
                if not t:
                    print('not found')
                else:
                    crud.delete_todo(s,t)
                    print('deleted')
            continue
        if cmd.startswith('update '):
            rest = cmd[len('update '):]
            parts = rest.split('|')
            if len(parts) < 2:
                print('usage: update <id>|<title>|<desc>')
                continue
            tid = parts[0].strip()
            title = parts[1].strip() if len(parts)>1 else ''
            desc = parts[2].strip() if len(parts)>2 else ''
            with get_session() as s:
                t = crud.get_todo(s, tid)
                if not t:
                    print('not found')
                else:
                    updated = crud.update_todo(s, t, TodoCreate(title=title or t.title, description=desc or t.description))
                    print('updated', updated.id)
            continue
        print('unknown command')

if __name__ == '__main__':
    repl()
