#!/bin/bash
export $(grep -v '^#' .env | xargs)
docker exec -it $PROJECT_NAME-api bash -c 'DJANGO_SUPERUSER_PASSWORD=1234 python manage.py createsuperuser --noinput --username admin --email admin@admin.com'