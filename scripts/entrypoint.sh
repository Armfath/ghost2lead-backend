#!/bin/sh
set -e
alembic upgrade head
python scripts/seed_admin.py ghost2lead-admin@yopmail.com
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
