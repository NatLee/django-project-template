#!/bin/bash

source "$(dirname "$0")/common.sh"

print_message "$RED" "This deletes every migration file of the project apps."
print_message "$YELLOW" "Only do this before your first deploy, then run: bash dev-tool.sh migration"
read -r -p "Type 'yes' to continue: " answer
if [ "$answer" != "yes" ]; then
    print_message "$BLUE" "Cancelled."
    exit 0
fi

# Run inside the container (as root), so no sudo is needed on the host.
docker exec "${CONTAINER_WEB_NAME}" bash -c \
    'find /app -path "*/migrations/*.py" -not -name "__init__.py" -delete && find /app -path "*/migrations/*.pyc" -delete'
print_message "$GREEN" "Migration files deleted."
