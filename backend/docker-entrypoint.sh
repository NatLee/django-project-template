#!/bin/bash
# Start-up for the backend-api container: migrate, collect static files, then run
# the web server and the task worker under supervisor.
set -euo pipefail

echo "=============== ${PROJECT_NAME:-django} backend ==============="

# Same parser as settings.py, so "true", "True", "1", "yes" all mean on.
if [ "$(python -c 'from backend.env import env_bool; print(env_bool("DEBUG"))')" = "True" ]; then
  echo "> DEBUG is on: runserver with auto-reload"
  export WEB_COMMAND="python manage.py runserver 0.0.0.0:8000"
else
  echo "> DEBUG is off: daphne"
  export WEB_COMMAND="daphne --bind 0.0.0.0 --port 8000 --proxy-headers backend.asgi:application"
fi

echo "> Applying migrations"
python manage.py migrate --noinput

echo "> Collecting static files"
python manage.py collectstatic --noinput --verbosity 0

echo "> Starting web server and task worker"
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
