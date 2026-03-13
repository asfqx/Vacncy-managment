# Vacancy Management

Платформа для поиска вакансий и резюме с разделением ролей на кандидата, работодателя и администратора.

Проект состоит из двух частей:
- `backend` — FastAPI, PostgreSQL, Redis, RabbitMQ, MinIO, Alembic, Ollama
- `frontend` — Vue 3 + Vite

## Возможности

- регистрация и авторизация пользователей
- роли: кандидат, работодатель, администратор
- создание и поиск вакансий
- создание и поиск резюме
- отклики на вакансии
- генерация сопроводительного письма через AI
- админ-панель для просмотра пользователей, вакансий, резюме и откликов
- загрузка аватаров в S3-совместимое хранилище

## Структура проекта

```text
Vacncy-managment/
|- backend/
|  |- docker-compose.yml
|  |- src/
|     |- app/
|     |- alembic/
|     |- pyproject.toml
|- frontend/
|  |- src/
|  |- package.json
|- .env.example
```

## Требования

Для локального запуска понадобятся:
- Python `3.13+`
- Node.js `20+`
- `uv`
- Docker Desktop
- Ollama

## Переменные окружения

В проекте используются несколько `.env` файлов.

### Корневой шаблон

В файле [`.env.example`](C:/Users/user/Desktop/диплом/Vacncy-managment/.env.example) лежит пример базовых переменных.

### Backend

Основной backend env находится в [`backend/src/.env`](C:/Users/user/Desktop/диплом/Vacncy-managment/backend/src/.env).

Ключевые переменные:

```env
APP_HOST=localhost
APP_PORT=8000

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=vacancy_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

CACHE_ADAPTER=redis
CACHE_ADAPTER_HOST=localhost
CACHE_ADAPTER_PORT=6379

AMQP_USER=guest
AMQP_PASSWORD=guest
AMQP_HOST=localhost
AMQP_PORT=5672

S3_PROVIDER=minio
S3_URL=localhost:9000
S3_ACCESS_KEY=USERNAME
S3_SECRET_KEY=PASSWORD

AI_MODEL_URL=http://localhost:11434
AI_MODEL_NAME=phi4-mini
```

### Frontend

Frontend env находится в [`frontend/.env`](C:/Users/user/Desktop/диплом/Vacncy-managment/frontend/.env).

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_S3_PUBLIC_BASE_URL=
```

## Запуск инфраструктуры

Из папки [`backend`](C:/Users/user/Desktop/диплом/Vacncy-managment/backend) поднимаются сервисы:
- PostgreSQL
- Redis
- RabbitMQ
- MinIO
- taskiq worker
- taskiq scheduler
- taskiq admin

Команда:

```powershell
cd backend
docker compose up -d
```

После запуска будут доступны:
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- RabbitMQ: `localhost:5672`
- RabbitMQ UI: `http://localhost:15672`
- MinIO API: `http://localhost:9000`
- MinIO Console: `http://localhost:9001`
- Taskiq Admin: `http://localhost:3000`

## Установка и запуск Ollama

AI-генерация откликов использует Ollama.

### 1. Установите Ollama

Скачать можно с официального сайта: [https://ollama.com/download](https://ollama.com/download)

После установки убедитесь, что Ollama запущена локально и доступна по адресу:

```text
http://localhost:11434
```

Именно этот адрес сейчас ожидается в backend env:
- `AI_MODEL_URL=http://localhost:11434`

### 2. Загрузите модель


```env
AI_MODEL_NAME=phi4-mini
```

Перед запуском генерации писем нужно скачать ее:

```powershell
ollama pull phi4-mini
```

### 3. Проверьте, что модель доступна

```powershell
ollama list
```

Если захочешь использовать другую модель, нужно:
- скачать ее через `ollama pull <model_name>`
- поменять `AI_MODEL_NAME` в [`backend/src/.env`](C:/Users/user/Desktop/диплом/Vacncy-managment/backend/src/.env)

## Запуск backend

Перейдите в [`backend/src`](C:/Users/user/Desktop/диплом/Vacncy-managment/backend/src):

```powershell
cd backend/src
```

### 1. Установите зависимости

```powershell
uv sync
```

### 2. Примените миграции

```powershell
uv run alembic upgrade head
```

### 3. Запустите backend

```powershell
uv run uvicorn app.main:app 
```

Backend будет доступен по адресу:
- API: [http://localhost:8000](http://localhost:8000)
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)

## Запуск frontend

Перейдите в [`frontend`](C:/Users/user/Desktop/диплом/Vacncy-managment/frontend):

```powershell
cd frontend
npm install
npm run dev
```

Frontend будет доступен по адресу:
- [http://localhost:5173](http://localhost:5173)

## Порядок локального запуска

Рекомендуемая последовательность:

1. Поднять инфраструктуру через `docker compose up -d` в `backend`
2. Убедиться, что запущена Ollama
3. Выполнить `ollama pull phi4-mini`
4. Установить зависимости backend через `uv sync`
5. Применить миграции `uv run alembic upgrade head`
6. Запустить backend
7. Установить зависимости frontend и запустить Vite

## Что использует backend

Основные библиотеки backend из [`pyproject.toml`](C:/Users/user/Desktop/диплом/Vacncy-managment/backend/src/pyproject.toml):
- FastAPI
- SQLAlchemy / asyncpg
- Alembic
- Redis
- Taskiq
- RabbitMQ
- MinIO
- Ollama
- Uvicorn

## Что использует frontend

Основные библиотеки frontend из [`package.json`](C:/Users/user/Desktop/диплом/Vacncy-managment/frontend/package.json):
- Vue 3
- Vue Router
- Pinia
- Axios
- Vite

## AI-функции в проекте

Сейчас Ollama используется для генерации сопроводительного письма при отклике на вакансию.

Для корректной работы должны одновременно выполняться условия:
- backend запущен
- Ollama запущена
- модель `phi4-mini` загружена
- в `backend/src/.env` корректно заполнены `AI_MODEL_URL` и `AI_MODEL_NAME`

## Лицензия

Проект распространяется под лицензией из файла [`LICENSE`](C:/Users/user/Desktop/диплом/Vacncy-managment/LICENSE).
