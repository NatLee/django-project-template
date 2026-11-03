#!/bin/bash
# Shared by the dev-*.sh scripts; dev-tool.sh exports the variables from .env first.

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Git Bash on Windows rewrites arguments that look like Unix paths (/app, /etc/...)
# into Windows paths before docker sees them; container paths must stay as they are.
export MSYS_NO_PATHCONV=1

# Container names follow PROJECT_NAME (see docker-compose.yml).
CONTAINER_WEB_NAME="${PROJECT_NAME}-api"
CONTAINER_NGINX_NAME="${PROJECT_NAME}-nginx"
SUPERVISOR_CONF=/etc/supervisor/conf.d/supervisord.conf

# Use a TTY only when there is one, so the scripts also work in CI and pipes.
if [ -t 0 ] && [ -t 1 ]; then
    DOCKER_EXEC_FLAGS=(-it)
else
    DOCKER_EXEC_FLAGS=(-i)
fi

print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}
