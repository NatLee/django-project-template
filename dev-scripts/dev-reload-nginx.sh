#!/bin/bash
source "$(dirname "$0")/common.sh"
print_message "$BLUE" "Reloading Nginx in ${CONTAINER_NGINX_NAME}..."

docker exec -it $CONTAINER_NGINX_NAME nginx -s reload