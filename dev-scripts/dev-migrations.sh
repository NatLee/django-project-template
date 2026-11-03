#!/bin/bash

source "$(dirname "$0")/common.sh"

print_message "$BLUE" "Creating and applying migrations in ${CONTAINER_WEB_NAME}..."
docker exec "${DOCKER_EXEC_FLAGS[@]}" "${CONTAINER_WEB_NAME}" bash -c 'python manage.py makemigrations && python manage.py migrate'
print_message "$GREEN" "Done. Commit the new files under */migrations/."
