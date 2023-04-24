#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "DB not yet run..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "DB did run."
fi

python manage.py flush --no-input
python manage.py migrate
python manage.py collectstatic
python manage.py loaddata app_goods_dump.json
python manage.py loaddata app_orders_dump.json
gunicorn marketplace.wsgi:application --bind 0.0.0.0:8000

exec "$@"