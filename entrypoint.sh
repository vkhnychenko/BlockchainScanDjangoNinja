#!/bin/sh

python manage.py migrate --no-input
python manage.py collectstatic --no-input

daphne -b 0.0.0.0 -p 8000 config.asgi:application