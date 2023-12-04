#!/bin/bash
echo "=============== Running docker-entrypoint.sh ==============="

DEBUG_="$(tr [A-Z] [a-z] <<<"$DEBUG")"

if [ "$DEBUG_" = false ]; then
    echo "> Waiting database starting"
    /wait
else
    echo "> Debug with SQLite."
fi

echo "> Django migrations"
python manage.py makemigrations
python manage.py migrate

echo "> Collect Static"
python manage.py collectstatic --noinput

echo "> Running server"
/usr/local/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
