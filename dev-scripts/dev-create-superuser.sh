#!/bin/bash

source "$(dirname "$0")/common.sh"

prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local input
    read -r -p "$prompt [$default]: " input
    echo "${input:-$default}"
}

USERNAME=$(prompt_with_default "Enter username" "admin")
EMAIL=$(prompt_with_default "Enter email" "admin@example.com")
read -r -s -p "Enter password: " PASSWORD
echo

print_message "$BLUE" "Creating superuser..."
# Pass the values as environment variables so quotes in them cannot break the command.
docker exec -e DJANGO_SUPERUSER_USERNAME="$USERNAME" -e DJANGO_SUPERUSER_EMAIL="$EMAIL" \
    -e DJANGO_SUPERUSER_PASSWORD="$PASSWORD" "${CONTAINER_WEB_NAME}" \
    python manage.py createsuperuser --noinput \
    && print_message "$GREEN" "Superuser created successfully."
