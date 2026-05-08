# Contacts Book API

REST API для управління контактами з аутентифікацією, побудований на FastAPI + PostgreSQL.

## Можливості

- CRUD операції з контактами (кожен користувач бачить лише свої)
- JWT аутентифікація (access + refresh token)
- Реєстрація з підтвердженням email
- Пошук контактів за ім'ям, прізвищем або email
- Отримання контактів з днем народження у найближчі 7 днів
- Завантаження аватару через Cloudinary
- Rate limiting (5 запитів/хвилину на `/api/users/me`)

## Вимоги

- Docker та Docker Compose
- Python 3.12+ (для локального запуску без Docker)

## Швидкий старт

### 1. Налаштування змінних оточення

Скопіюйте `.env.example` у `.env` та заповніть реальними значеннями:

```bash
cp .env.example .env
```

Ключові змінні:
| Змінна | Опис |
|---|---|
| `DB_URL` | URL підключення до PostgreSQL |
| `JWT_SECRET` | Секретний ключ для підпису JWT токенів |
| `JWT_ALGORITHM` | Алгоритм підпису (за замовчуванням `HS256`) |
| `JWT_EXPIRATION_TIME` | Час життя access token у секундах |
| `MAIL_*` | Налаштування SMTP для відправки email |
| `CLOUDINARY_*` | Credentials для завантаження аватарів |

### 2. Запуск через Docker Compose

```bash
docker-compose up --build
```

Це запустить:
- **web** — FastAPI застосунок на `http://localhost:3000`
- **db** — PostgreSQL на порту `5432`

Міграції застосовуються автоматично при старті контейнера.

### 3. Перевірка роботи API

Відкрийте Swagger UI: **http://localhost:3000/docs**

## API Ендпоінти

### Auth (`/api/auth`)

| Метод | Шлях | Опис |
|---|---|---|
| `POST` | `/signup` | Реєстрація нового користувача |
| `POST` | `/login` | Логін (повертає `access_token`) |
| `GET` | `/refresh_token` | Оновлення пари токенів (передати refresh token в `Authorization: Bearer <token>`) |
| `GET` | `/confirmed_email/{token}` | Підтвердження email |
| `POST` | `/request_email` | Повторна відправка листа підтвердження |

### Contacts (`/api/contacts`)

> Усі ендпоінти вимагають `Authorization: Bearer <access_token>`

| Метод | Шлях | Опис |
|---|---|---|
| `GET` | `/` | Список контактів (з фільтрами `first_name`, `last_name`, `email`) |
| `POST` | `/` | Створити контакт |
| `GET` | `/{contact_id}` | Отримати контакт за ID |
| `PUT` | `/{contact_id}` | Оновити контакт |
| `DELETE` | `/{contact_id}` | Видалити контакт |
| `GET` | `/birthdays` | Контакти з днем народження у найближчі 7 днів |

### Users (`/api/users`)

| Метод | Шлях | Опис |
|---|---|---|
| `GET` | `/me` | Поточний користувач (rate limited: 5/хв) |
| `PATCH` | `/avatar` | Оновити аватар (upload файлу) |

## Корисні команди Docker

```bash
# Запуск
docker-compose up --build

# Запуск у фоні
docker-compose up -d --build

# Перегляд логів
docker-compose logs -f web

# Створення нової міграції
docker-compose exec web alembic revision --autogenerate -m "опис міграції"

# Застосування міграцій вручну
docker-compose exec web alembic upgrade head

# Зупинка
docker-compose down

# Зупинка з видаленням даних БД
docker-compose down -v
```

## Структура проєкту

```
├── main.py                  # Точка входу FastAPI
├── docker-compose.yml       # Docker конфігурація
├── Dockerfile
├── alembic.ini              # Конфігурація Alembic
├── migrations/              # Міграції бази даних
└── src/
    ├── api/                 # Роутери (auth, contacts, users, utils)
    ├── conf/                # Конфігурація та rate limiter
    ├── database/            # Моделі та підключення до БД
    ├── repository/          # Репозиторії (робота з БД)
    ├── schemas/             # Pydantic-схеми
    └── services/            # Бізнес-логіка (auth, email, upload)
```