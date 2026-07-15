#!/usr/bin/env bash
# Render build script: installs deps, collects static files, applies migrations.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate

python manage.py ensure_superuser
