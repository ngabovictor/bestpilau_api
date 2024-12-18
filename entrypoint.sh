#!/bin/bash
APP_PORT=${PORT:-8000}
cd /app/
/opt/venv/bin/python manage.py migrate --noinput
/opt/venv/bin/python manage.py collectstatic --noinput
#/opt/venv/bin/gunicorn --worker-tmp-dir /dev/shm dropahub_api.wsgi:application --bind "0.0.0.0:${APP_PORT}"
/opt/venv/bin/uvicorn bestpilau_api.asgi:application --host 0.0.0.0 --port "${APP_PORT}" --workers 4