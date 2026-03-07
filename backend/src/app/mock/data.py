from typing import Any
import random


def build_mock_vacancies(seed: int = 42) -> list[dict[str, Any]]:
    rnd = random.Random(seed)

    cities = [
        "Москва", "Санкт-Петербург", "Казань", "Екатеринбург", "Новосибирск",
        "Нижний Новгород", "Самара", "Ростов-на-Дону", "Краснодар", "Воронеж",
        "Пермь", "Уфа", "Челябинск", "Омск", "Красноярск", "Владивосток",
        "Тюмень", "Ижевск", "Томск", "Иркутск",
    ]

    roles = [
        "Backend-разработчик", "Frontend-разработчик", "Fullstack-разработчик",
        "Python-разработчик", "Java-разработчик", "Go-разработчик",
        "PHP-разработчик", "Node.js-разработчик", "Android-разработчик",
        "iOS-разработчик", "DevOps-инженер", "SRE-инженер",
        "Data Engineer", "ML-инженер", "Data Analyst",
        "QA-инженер", "QA Automation", "Системный аналитик",
        "Бизнес-аналитик", "Product Analyst",
        "Инженер по информационной безопасности", "Администратор баз данных",
        "Инженер поддержки (L2/L3)", "UX/UI дизайнер",
    ]

    specialties = [
        "для финтех-платформы", "для маркетплейса", "для ERP-системы",
        "для мобильного банка", "для логистической платформы",
        "для HR-сервиса", "для CRM", "для EdTech-проекта",
        "для IoT-продукта", "для медтех-сервиса",
        "для системы рекомендаций", "для аналитической витрины",
        "для платформы вакансий", "для онлайн-кинотеатра",
        "для сервиса доставки", "для телеком-продукта",
        "для платежного шлюза", "для рекламного кабинета",
        "для B2B-портала", "для платформы мониторинга",
    ]

    levels = ["Junior", "Junior+", "Middle", "Middle+", "Senior"]
    formats = ["Офис", "Гибрид", "Удалённо"]
    employments = ["Полная занятость", "Частичная занятость", "Проектная работа"]

    tech_blocks = {
        "backend_py": ["Python", "FastAPI", "Django", "SQLAlchemy", "AsyncIO", "PostgreSQL", "Redis", "Celery", "RabbitMQ", "Kafka"],
        "backend_java": ["Java", "Spring Boot", "Hibernate", "PostgreSQL", "Kafka", "Redis", "Liquibase", "JUnit"],
        "backend_go": ["Go", "Gin", "gRPC", "PostgreSQL", "Redis", "Kafka", "Prometheus"],
        "backend_node": ["Node.js", "NestJS", "TypeScript", "PostgreSQL", "Redis", "Kafka", "BullMQ"],
        "frontend_vue": ["Vue 3", "TypeScript", "Pinia", "Vite", "Vue Router", "REST", "OpenAPI"],
        "frontend_react": ["React", "TypeScript", "Redux Toolkit", "Vite", "React Query", "REST", "Storybook"],
        "mobile_android": ["Kotlin", "Android", "Coroutines", "Room", "Retrofit", "Compose"],
        "mobile_ios": ["Swift", "iOS", "SwiftUI", "Combine", "CoreData"],
        "devops": ["Linux", "Docker", "Kubernetes", "Helm", "GitLab CI", "Prometheus", "Grafana", "Terraform"],
        "qa_auto": ["Python", "Pytest", "Playwright", "Selenium", "Allure", "CI/CD"],
        "data_eng": ["SQL", "Airflow", "Python", "Spark", "Kafka", "DWH", "dbt"],
        "ml": ["Python", "Pandas", "PyTorch", "Sklearn", "MLflow", "Docker"],
        "analyst": ["SQL", "Power BI", "Tableau", "A/B-тесты", "Продуктовые метрики"],
        "sec": ["SIEM", "WAF", "OWASP", "Логи", "Incident Response", "Threat Modeling"],
        "dba": ["PostgreSQL", "Репликация", "Бэкапы", "Оптимизация запросов", "Мониторинг"],
        "support": ["Linux", "Сети", "SQL", "Логи", "SLA", "Траблшутинг"],
        "sa": ["UML", "BPMN", "User Stories", "SQL", "Интеграции", "API"],
        "design": ["Figma", "UX-исследования", "Дизайн-системы", "Прототипирование", "HIG/Material"],
    }

    role_to_blocks = {
        "Backend-разработчик": ["backend_py", "backend_java", "backend_go", "backend_node"],
        "Python-разработчик": ["backend_py", "qa_auto", "data_eng", "ml"],
        "Java-разработчик": ["backend_java"],
        "Go-разработчик": ["backend_go"],
        "Node.js-разработчик": ["backend_node"],
        "Frontend-разработчик": ["frontend_vue", "frontend_react"],
        "Fullstack-разработчик": ["frontend_react", "frontend_vue", "backend_node", "backend_py"],
        "Android-разработчик": ["mobile_android"],
        "iOS-разработчик": ["mobile_ios"],
        "DevOps-инженер": ["devops"],
        "SRE-инженер": ["devops"],
        "QA Automation": ["qa_auto"],
        "QA-инженер": ["qa_auto"],
        "Data Engineer": ["data_eng"],
        "ML-инженер": ["ml", "data_eng"],
        "Data Analyst": ["analyst"],
        "Product Analyst": ["analyst"],
        "Системный аналитик": ["sa"],
        "Бизнес-аналитик": ["sa"],
        "Инженер по информационной безопасности": ["sec"],
        "Администратор баз данных": ["dba"],
        "Инженер поддержки (L2/L3)": ["support"],
        "UX/UI дизайнер": ["design"],
    }

    responsibilities_pool = [
        "проектировать и развивать функциональность продукта",
        "писать и поддерживать REST/gRPC API",
        "оптимизировать производительность и устранение узких мест",
        "участвовать в code review и улучшать качество кода",
        "настраивать мониторинг, алертинг и метрики",
        "интегрировать внешние сервисы и платежные системы",
        "работать с очередями и асинхронной обработкой",
        "улучшать UX совместно с дизайнером и аналитиками",
        "автоматизировать тестирование и релизные процессы",
        "участвовать в декомпозиции задач и оценке сроков",
        "вести техническую документацию",
        "обеспечивать надежность и отказоустойчивость",
    ]

    bonus_pool = [
        "опыт с микросервисной архитектурой",
        "знание Domain-Driven Design",
        "опыт в highload",
        "понимание информационной безопасности",
        "опыт работы с брокерами сообщений (Kafka/RabbitMQ)",
        "навыки работы с профилировщиками",
        "опыт построения дизайн-систем",
        "опыт работы с ClickHouse",
        "опыт построения ETL/ELT",
        "опыт с Sentry/Jaeger/Tracing",
        "опыт с GraphQL",
        "опыт с pgvector/семантическим поиском",
    ]

    offers_pool = [
        "гибкий график и понятные процессы",
        "компенсация обучения и конференций",
        "ДМС после испытательного срока",
        "техника для работы и корпоративные скидки",
        "прозрачные грейды и пересмотр зарплаты",
        "дружная команда и наставничество",
        "возможность влияния на продуктовые решения",
        "оплачиваемые отпуска и больничные",
    ]

    # Диапазоны зарплат по “уровню”
    level_salary = {
        "Junior": (70000, 110000),
        "Junior+": (90000, 140000),
        "Middle": (130000, 220000),
        "Middle+": (180000, 280000),
        "Senior": (240000, 420000),
    }

    # Чтобы все названия были уникальными, используем комбинации + #i
    used_titles: set[str] = set()
    vacancies: list[dict[str, Any]] = []

    for i in range(1, 101):
        role = rnd.choice(roles)
        level = rnd.choice(levels)
        spec = rnd.choice(specialties)

        # Уникальный заголовок
        title_variants = [
            f"{role} {level} {spec}",
            f"{level} {role} {spec}",
            f"{role} ({level}) {spec}",
            f"{role} {spec} — {level}",
        ]
        title = rnd.choice(title_variants)
        # гарантируем уникальность
        if title in used_titles:
            title = f"{title} #{i}"
        used_titles.add(title)

        # Техстек
        blocks = role_to_blocks.get(role, ["backend_py"])
        chosen_blocks = rnd.sample(blocks, k=min(len(blocks), rnd.randint(1, 2)))
        tech = []
        for b in chosen_blocks:
            tech.extend(tech_blocks[b])
        tech = list(dict.fromkeys(tech))
        rnd.shuffle(tech)
        tech = tech[: rnd.randint(6, 10)]

        resp = rnd.sample(responsibilities_pool, k=5)
        bonus = rnd.sample(bonus_pool, k=3)

        fmt = rnd.choice(formats)
        remote = fmt == "Удалённо" or (fmt == "Гибрид" and rnd.random() < 0.4)

        city = rnd.choice(cities) if not remote else rnd.choice([*cities[:5], "Удалённо"])

        lo, hi = level_salary[level]
        salary = rnd.randrange(lo, hi + 1, 5000)

        product_context = rnd.choice([
            "высоконагруженный сервис с миллионами событий в сутки",
            "B2B-продукт с интеграциями и сложными бизнес-процессами",
            "платформа с личными кабинетами и сложной авторизацией",
            "сервис рекомендаций и персонализации выдачи",
            "внутренняя система автоматизации для бизнеса",
            "продукт с публичным API для партнёров",
            "приложение с упором на безопасность и аудит",
            "витрина данных и аналитика для продуктовых команд",
        ])

        employment = rnd.choice(employments)
        offers = rnd.sample(offers_pool, k=4)

        description = f"""
Мы развиваем {product_context}. Нужен(на) {role.lower()} уровня {level}.

Обязанности:
- {resp[0].capitalize()}
- {resp[1].capitalize()}
- {resp[2].capitalize()}
- {resp[3].capitalize()}
- {resp[4].capitalize()}

Требования:
- коммерческий опыт от {1 if level.startswith("Junior") else 2 if "Middle" in level else 4} лет (или сопоставимый уровень);
- уверенное владение: {", ".join(tech[:4])};
- практический опыт с: {", ".join(tech[4:])};
- аккуратность к качеству кода, тестам и документации.

Будет плюсом:
- {bonus[0].capitalize()}
- {bonus[1].capitalize()}
- {bonus[2].capitalize()}

Условия:
- формат: {fmt};
- занятость: {employment};
- понятные задачи и поддержка команды.

Мы предлагаем:
- {offers[0].capitalize()}
- {offers[1].capitalize()}
- {offers[2].capitalize()}
- {offers[3].capitalize()}
""".strip()

        vacancies.append(
            {
                "title": title,
                "description": description,
                "city": city,
                "remote": remote,
                "salary": salary,
                "currency": "RUB",
            }
        )

    return vacancies


MOCK_VACANCIES: list[dict[str, Any]] = build_mock_vacancies()