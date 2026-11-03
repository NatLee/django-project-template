#!/bin/bash

source "$(dirname "$0")/common.sh"

print_message "$BLUE" "Starting Supervisor control shell in ${CONTAINER_WEB_NAME}..."
docker exec "${DOCKER_EXEC_FLAGS[@]}" "${CONTAINER_WEB_NAME}" supervisorctl -c "$SUPERVISOR_CONF" "$@"
