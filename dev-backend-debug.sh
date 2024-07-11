#!/bin/bash
export $(grep -v '^#' .env | xargs)
docker exec -it $PROJECT_NAME-api bash -c "supervisorctl -c /etc/supervisor/conf.d/supervisord.conf stop django"
docker exec -it $PROJECT_NAME-api bash -c "python manage.py runserver 0.0.0.0:8000"