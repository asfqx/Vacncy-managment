from typing import Any


MOCK_VACANCIES: list[dict[str, Any]] = [
    {
        "title": f"Backend Developer Python #{i}",
        "description": f"""
Мы ищем Backend-разработчика уровня Middle/Senior.

Обязанности:
- Разработка REST API на FastAPI
- Работа с PostgreSQL и Redis
- Проектирование архитектуры сервисов
- Оптимизация запросов и производительности

Требования:
- Опыт Python от 2 лет
- Знание SQLAlchemy
- Понимание принципов REST
- Опыт работы с Docker

Будет плюсом:
- Elasticsearch
- Celery / TaskIQ
- Kubernetes

Мы предлагаем:
- Гибкий график
- Возможность удаленной работы
- Конкурентную заработную плату
""",
        "city": "Москва" if i % 3 == 0 else "Санкт-Петербург",
        "remote": i % 2 == 0,
        "salary": 150000 + i * 1000,
        "currency": "RUB",
    }
    for i in range(1, 51)
] + [
    {
        "title": f"Frontend Developer Vue.js #{i}",
        "description": f"""
Мы ищем Frontend-разработчика.

Обязанности:
- Разработка SPA на Vue 3
- Работа с Pinia
- Интеграция с REST API
- Оптимизация UX

Требования:
- Опыт Vue.js от 1 года
- Понимание Composition API
- Опыт работы с TypeScript
- Опыт верстки

Будет плюсом:
- Nuxt
- Vite
- Опыт работы с дизайн-системами

Мы предлагаем:
- Удаленная работа
- ДМС
- Гибкий график
""",
        "city": "Казань" if i % 2 == 0 else "Екатеринбург",
        "remote": True,
        "salary": 120000 + i * 800,
        "currency": "RUB",
    }
    for i in range(51, 101)
]
