FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    gettext \
    bash \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Копирование и установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Копирование entrypoint ПЕРВЫМ
COPY docker-entrypoint.sh .

# Копирование исходного кода
COPY src/ .

# Права на выполнение entrypoint
RUN chmod +x docker-entrypoint.sh

# Создание директорий для статики и медиа
RUN mkdir -p /app/staticfiles /app/media

EXPOSE 8000

# Использование entrypoint - ВАЖНО: shell форма
CMD ["bash", "./docker-entrypoint.sh"]