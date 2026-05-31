#!/bin/sh

# Inicialização de produção no Render.
# Render injeta a porta em $PORT; o serviço web deve escutar nela.

set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn project.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 3 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile -
