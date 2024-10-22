#!/bin/bash

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Constant: container names for Web
CONTAINER_WEB_NAME="${PROJECT_NAME}-api"

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to execute scripts
execute_script() {
    local script=$1
    shift
    if [ -f "./dev-scripts/$script.sh" ]; then
        bash "./dev-scripts/$script.sh" "$@"
    else
        print_message "$RED" "Error: Script $script not found."
        exit 1
    fi
}

# Main script logic
case "$1" in
    create-superuser)
        shift
        execute_script "dev-create-superuser" "$@"
        ;;
    shell)
        shift
        print_message "$YELLOW" "Starting Web Server container shell..."
        execute_script "dev-bash" "$@"
        ;;
    ipython)
        shift
        execute_script "dev-shell" "$@"
        ;;
    supervisorctl)
        shift
        execute_script "dev-supervisorctl" "$@"
        ;;
    migration)
        shift
        execute_script "dev-migrations" "$@"
        ;;
    backend-debug)
        shift
        execute_script "dev-backend-debug" "$@"
        ;;
    collect-static)
        shift
        execute_script "dev-collect-statics" "$@"
        ;;
    django-startapp)
        shift
        execute_script "dev-startapp" "$@"
        ;;
    reload-ngnix)
        shift
        execute_script "dev-reload-nginx" "$@"
        ;;
    clean-migrations)
        shift
        execute_script "dev-clean-migrations" "$@"
        ;;
    *)
        print_message "$YELLOW" "Usage: $0 sub-command [args]"
        print_message "$BLUE" "Sub-commands:"
        print_message "$GREEN" "  create-superuser: Create an admin account for management."
        print_message "$GREEN" "  shell: Create a shell to run arbitrary command."
        print_message "$GREEN" "  ipython: Create a shell to run ipython."
        print_message "$GREEN" "  supervisorctl: Attach to supervisor control shell."
        print_message "$GREEN" "  migration: Run migration process."
        print_message "$GREEN" "  backend-debug: Recreate and attach to backend container."
        print_message "$GREEN" "  collect-static: Collect static files to increase rendering speed."
        print_message "$GREEN" "  django-startapp: Create a new Django app."
        print_message "$GREEN" "  reload-nginx: Reload Nginx configuration."
        print_message "$GREEN" "  clean-migrations: Clean up migration files."
        ;;
esac