#!/bin/bash

source "$(dirname "$0")/common.sh"
print_message "$BLUE" "Executing command in ${CONTAINER_WEB_NAME}..."

# Run the given command, or open a bash shell when there is none.
if [ $# -gt 0 ]; then
    docker exec "${DOCKER_EXEC_FLAGS[@]}" "${CONTAINER_WEB_NAME}" "$@"
else
    docker exec "${DOCKER_EXEC_FLAGS[@]}" "${CONTAINER_WEB_NAME}" bash
fi
