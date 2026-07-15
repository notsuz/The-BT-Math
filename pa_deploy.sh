#!/usr/bin/env bash
# Run manually in a PythonAnywhere Bash console (with the venv active) after
# `git pull` - PythonAnywhere has no automatic build step like Render does.
set -o errexit

# --no-cache-dir: PythonAnywhere's free tier has a tight 512MB disk quota,
# and pip's download cache alone can push past it, breaking future installs
# (pip then fails to even create a temp dir). psycopg2-binary is dropped
# here since PythonAnywhere uses SQLite, not Postgres - Render's build.sh
# still installs the full requirements.txt as-is.
pip install --no-cache-dir --no-compile -r <(grep -v '^psycopg2-binary' requirements.txt)

python manage.py collectstatic --noinput
python manage.py migrate

python manage.py ensure_superuser
python manage.py seed_demo
