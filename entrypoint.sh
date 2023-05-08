#!/bin/sh
set -e

echo "${0}: running migrations."
python3 manage.py migrate
echo "${0}: starting application."
gunicorn -c gunicorn_conf.py api.main:app