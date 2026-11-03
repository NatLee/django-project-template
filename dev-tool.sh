#!/bin/bash
# Shortcuts for working with the running containers. Run from the project root:
#   bash dev-tool.sh <command> [args]

cd "$(dirname "$0")" || exit 1

if [ ! -f .env ]; then
    echo "No .env found. Create one first: cp .env.example .env" >&2
    exit 1
fi
# Export every variable in .env (PROJECT_NAME decides the container names).
set -a
# shellcheck disable=SC1091
. ./.env
set +a

source ./dev-scripts/common.sh

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

usage() {
    print_message "$YELLOW" "Usage: $0 <command> [args]"
    print_message "$BLUE" "Commands:"
    print_message "$GREEN" "  create-superuser   Create an admin account."
    print_message "$GREEN" "  shell [cmd...]     Open a bash shell in the backend container, or run a command there."
    print_message "$GREEN" "  ipython            Open the Django shell (IPython)."
    print_message "$GREEN" "  supervisorctl      Attach to supervisor (web server + task worker)."
    print_message "$GREEN" "  migration          Create and apply migrations after you change models."
    print_message "$GREEN" "  test [args...]     Run the test suite (pytest) in the backend container."
    print_message "$GREEN" "  backend-debug      Run Django in the foreground so breakpoints (ipdb) work."
    print_message "$GREEN" "  collect-static     Collect static files."
    print_message "$GREEN" "  django-startapp    Create a new Django app: django-startapp <name>."
    print_message "$GREEN" "  reload-nginx       Reload the NGINX configuration."
    print_message "$GREEN" "  clean-migrations   Delete all migration files (only before your first deploy)."
}

command=$1
shift
case "$command" in
    create-superuser) execute_script "dev-create-superuser" "$@" ;;
    shell)
        print_message "$YELLOW" "Starting backend container shell..."
        execute_script "dev-bash" "$@"
        ;;
    ipython) execute_script "dev-shell" "$@" ;;
    supervisorctl) execute_script "dev-supervisorctl" "$@" ;;
    migration) execute_script "dev-migrations" "$@" ;;
    test) execute_script "dev-test" "$@" ;;
    backend-debug) execute_script "dev-backend-debug" "$@" ;;
    collect-static) execute_script "dev-collect-statics" "$@" ;;
    django-startapp) execute_script "dev-startapp" "$@" ;;
    # "reload-ngnix" was the only spelling that worked before; keep it so old notes still work.
    reload-nginx | reload-ngnix) execute_script "dev-reload-nginx" "$@" ;;
    clean-migrations) execute_script "dev-clean-migrations" "$@" ;;
    *) usage ;;
esac
