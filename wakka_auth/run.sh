#!/bin/sh

set -x
set -e

python manage.py collectstatic --noinput
python manage.py migrate

python -m gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 6 --log-level=debug