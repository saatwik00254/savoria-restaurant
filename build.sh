#!/usr/bin/env bash
# Render build script — runs before each deploy

set -o errexit   # exit on any error

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Load fixtures only on first deploy (skip if data already exists)
python manage.py shell -c "
from menu.models import Category
if not Category.objects.exists():
    import subprocess
    subprocess.run(['python', 'manage.py', 'loaddata', 'menu/fixtures/initial_data.json'])
    print('Fixtures loaded.')
else:
    print('Data already exists — skipping fixtures.')
"
