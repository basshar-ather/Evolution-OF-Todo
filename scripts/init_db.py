"""Initialize the application's database using the configured DATABASE_URL.

Usage: set the env var `DATABASE_URL` (optional) and run this script.
Example:
  $env:DATABASE_URL = 'postgresql://user:pass@host:5432/db'
  python .\scripts\init_db.py
"""
import os
import sys

# Ensure repo path imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'phases', 'phase-1', 'backend')))

from app.database import init_db


def main():
    db_url = os.environ.get('DATABASE_URL')
    print(f"Initializing DB (DATABASE_URL={db_url or '<default sqlite>'})")
    init_db(url=db_url)


if __name__ == '__main__':
    main()
