#!/bin/bash
source "$(dirname "$0")/common.sh"
print_message "$RED" "Deleting migrations files in ${CONTAINER_WEB_NAME}..."

# Delete migrations
sudo find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
sudo find . -path "*/migrations/*.pyc"  -delete