#!/bin/bash
echo "Running docker entrypoint script"
python manage.py makemigrations --noinput
python manage.py migrate --noinput
#python manage.py collectstatic --noinput
#python manage.py crontab add && cron start
DJANGO_SUPERUSER_PASSWORD=$DJANGO_SUPERUSER_PASSWORD python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL
python manage.py runserver 0.0.0.0:8000