FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock* ./

# Устанавливаем Poetry и зависимости
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Копируем остальной код
COPY . .

# Запускаем через модуль
CMD ["python", "-m", "etl_project.main"]