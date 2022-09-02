#!/bin/bash

DEBUG_="$(tr [A-Z] [a-z] <<< "$DEBUG")"

if [ "$DEBUG_" = false ] ; then
    echo "--------------- Waiting database starting"
    /wait
else
    echo "--------------- Debug with SQLite."
fi

echo "--------------- Running docker entrypoint script"
echo "--------------- Running Django migrations"
python manage.py makemigrations
python manage.py migrate
echo "--------------- Creating Superuser"
DJANGO_SUPERUSER_PASSWORD=$DJANGO_SUPERUSER_PASSWORD python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL
echo "--------------- Running server"
python manage.py runserver 0.0.0.0:8000