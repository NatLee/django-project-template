#!/bin/bash

source "$(dirname "$0")/common.sh"

print_message "$BLUE" "Collecting static files in ${CONTAINER_WEB_NAME}..."
docker exec "${DOCKER_EXEC_FLAGS[@]}" "${CONTAINER_WEB_NAME}" python manage.py collectstatic --noinput
print_message "$GREEN" "Static files collected successfully."
