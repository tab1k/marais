#!/bin/bash
set -e

echo "=== Starting Marais ==="

# Простая проверка базы данных
echo "Waiting for database..."
for i in {1..30}; do
  if python -c "
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marais.settings.production')
import django
try:
    django.setup()
    from django.db import connection
    connection.ensure_connection()
    print('OK')
except Exception as e:
    print(f'DB Connection Error: {e}', file=sys.stderr)
    sys.exit(1)
  "; then
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

# Оптимизация изображений (non-blocking)
if command -v python >/dev/null 2>&1; then
  echo "Optimizing images..."
  python /app/optimize_images.py || echo "Image optimization skipped"
fi

# Импорт товаров из Google Таблиц
if [ "${CLEAR_CATALOG_ON_START}" = "1" ] || [ "${CLEAR_CATALOG_ON_START}" = "true" ]; then
  echo "Clearing catalog data before import..."
  python manage.py shell -c "from catalog.models import ProductImage, Product, Category, Brand, Collection; ProductImage.objects.all().delete(); Product.objects.all().delete(); Category.objects.all().delete(); Brand.objects.all().delete(); Collection.objects.all().delete(); print('Catalog cleared')"
fi

echo "Importing products from Google Sheets..."
python import_products.py

# Запуск
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 marais.wsgi:application
