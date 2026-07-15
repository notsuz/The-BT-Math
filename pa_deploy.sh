#!/usr/bin/env bash
# Run manually in a PythonAnywhere Bash console (with the venv active) after
# `git pull` - PythonAnywhere has no automatic build step like Render does.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate

python manage.py ensure_superuser
python manage.py seed_demo
