#!/bin/bash

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Constant
CONTAINER_WEB_NAME="${PROJECT_NAME}-api"
CONTAINER_NGINX_NAME="${PROJECT_NAME}-nginx"

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}