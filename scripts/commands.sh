#!/bin/sh

set -e

if [ -n "$POSTGRES_HOST" ] && [ -n "$POSTGRES_PORT" ]; then
  while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
    echo "🟡 Waiting for Postgres Database Startup ($POSTGRES_HOST $POSTGRES_PORT) ..."
    sleep 2
  done
  echo "✅ Postgres Database Started Successfully ($POSTGRES_HOST:$POSTGRES_PORT)"
else
  echo "⚠️  POSTGRES_HOST or POSTGRES_PORT not set — skipping database wait."
fi

python manage.py compilemessages --locale pt_BR
python manage.py collectstatic --noinput
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8000
