#!/bin/bash

source "$(dirname "$0")/common.sh"

if [ -z "$1" ]; then
  print_message "$RED" "Error: App name is required."
  print_message "$YELLOW" "Usage: bash dev-tool.sh django-startapp <app_name>"
  exit 1
fi

APP_NAME="$1"

print_message "$BLUE" "Creating new Django app '${APP_NAME}' in ${CONTAINER_WEB_NAME}..."
docker exec "${CONTAINER_WEB_NAME}" python manage.py startapp "${APP_NAME}"

if [ ! -d "./backend/${APP_NAME}" ]; then
  print_message "$RED" "Error: Folder not created."
  exit 1
fi

# The container runs as root; hand the new files to you (the backend folder is mounted at /app).
print_message "$YELLOW" "Adjusting permissions for the new app folder..."
docker exec "${CONTAINER_WEB_NAME}" chown -R "$(id -u):$(id -g)" "/app/${APP_NAME}"

print_message "$GREEN" "New Django app '${APP_NAME}' created. Add it to INSTALLED_APPS in backend/backend/settings.py."
