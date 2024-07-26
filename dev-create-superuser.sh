#!/bin/bash

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Function to prompt for input with a default value
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local input

    read -p "$prompt [$default]: " input
    echo "${input:-$default}"
}

# Get user input
USERNAME=$(prompt_with_default "Enter username" "admin")
EMAIL=$(prompt_with_default "Enter email" "admin@admin.com")
PASSWORD=$(prompt_with_default "Enter password" "1234")

# Create superuser
docker exec -it $PROJECT_NAME-api bash -c "DJANGO_SUPERUSER_PASSWORD='$PASSWORD' python manage.py createsuperuser --noinput --username '$USERNAME' --email '$EMAIL'"

echo "Superuser created successfully!"