#!/bin/bash

source "$(dirname "$0")/common.sh"
print_message "$BLUE" "Executing command in ${CONTAINER_WEB_NAME}..."

# 如果有傳遞參數，則執行這些參數作為命令
if [ $# -gt 0 ]; then
    docker exec -it ${CONTAINER_WEB_NAME} "$@"
else
    # 如果沒有參數，則只是進入容器的 bash shell
    docker exec -it ${CONTAINER_WEB_NAME} bash
fi
