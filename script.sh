#!/usr/bin/env bash
VENV_DIR="./venv"
if [ ! -d "$VENV_DIR" ]; then
    python -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn lic_api.wsgi:application --bind 0.0.0.0:80 --workers 3


