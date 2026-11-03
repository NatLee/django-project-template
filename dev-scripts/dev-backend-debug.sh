#!/bin/bash

source "$(dirname "$0")/common.sh"

print_message "$BLUE" "Starting backend debug process..."

# Stop the Django process that supervisor manages, then run one in the foreground
# so breakpoint()/ipdb can take over this terminal.
supervisor_status=$(docker exec "${CONTAINER_WEB_NAME}" supervisorctl -c "$SUPERVISOR_CONF" status django)

if [[ $supervisor_status == *"RUNNING"* ]]; then
  print_message "$YELLOW" "Supervisor is running Django, stopping it..."
  docker exec "${CONTAINER_WEB_NAME}" supervisorctl -c "$SUPERVISOR_CONF" stop django
else
  print_message "$YELLOW" "Supervisor is not running Django, checking for manually started Django..."
  django_pid=$(docker exec "${CONTAINER_WEB_NAME}" bash -c "pgrep -f 'manage.py runserver' || true")
  if [ -n "$django_pid" ]; then
    print_message "$YELLOW" "Found manually started Django (PID: $django_pid), stopping it..."
    docker exec "${CONTAINER_WEB_NAME}" kill $django_pid
  else
    print_message "$YELLOW" "No running Django instance found."
  fi
fi

print_message "$BLUE" "Waiting for Django to stop completely..."
sleep 5

print_message "$GREEN" "Starting new Django instance (Ctrl+C to stop; then run: bash dev-tool.sh supervisorctl start django)..."
docker exec -it "${CONTAINER_WEB_NAME}" python manage.py runserver 0.0.0.0:8000
