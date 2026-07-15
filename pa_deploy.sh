#!/usr/bin/env bash
# Run manually in a PythonAnywhere Bash console (with the venv active) after
# `git pull` - PythonAnywhere has no automatic build step like Render does.
set -o errexit

# PythonAnywhere's free-tier sandboxing can block Python's tempfile module
# from writing to /tmp even though plain shell commands (e.g. `touch`) work
# fine there, which makes pip fail with "No usable temporary directory
# found". Point it at a folder inside the home dir instead.
export TMPDIR="$HOME/tmp"
mkdir -p "$TMPDIR"

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
