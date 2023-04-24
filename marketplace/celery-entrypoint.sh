#!/bin/sh

until cd /usr/src/app
do
    echo "Waiting for server volume..."
done

celery -A marketplace worker -l info
