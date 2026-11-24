#!/bin/sh
set -eu
exec gunicorn website.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 30 --graceful-timeout 30 --keep-alive 5 --no-control-socket --max-requests 1000 --max-requests-jitter 100 --access-logfile - --error-logfile -
