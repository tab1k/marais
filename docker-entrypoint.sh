#!/bin/bash
set -e

echo "=== Starting Marais ==="

# Простая проверка базы данных
echo "Waiting for database..."
for i in {1..30}; do
  if python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trucking_desk.settings')
import django
django.setup()
from django.db import connection
connection.ensure_connection()
print('OK')
  " 2>/dev/null; then
    echo "Database connected"
    break
  fi
  echo "Attempt $i/30..."
  sleep 2
  if [ $i -eq 30 ]; then
    echo "Database timeout!"
    exit 1
  fi
done

# Миграции
echo "Running migrations..."
python manage.py migrate

# Статика
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Запуск
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 trucking_desk.wsgi:application