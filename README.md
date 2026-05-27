# Image Hosting

Веб-сервис для загрузки и хранения изображений. Файлы сохраняются на диск, метаданные — в PostgreSQL. Статика и медиа отдаются через Nginx, API и HTML-страницы — через Python HTTP-сервер.

## Возможности

- Загрузка изображений (JPG, JPEG, PNG, GIF) с проверкой типа и размера
- Просмотр списка загруженных файлов с пагинацией
- Прямые ссылки на картинки (`/images/<filename>.<ext>`)
- Удаление изображений (файл + запись в БД)

## Стек

- **Python 3.13** — `http.server`, обработчики в `app/`
- **PostgreSQL 17** — хранение метаданных
- **Nginx** — статика, медиа, reverse proxy
- **Pillow** — валидация изображений
- **psycopg 3** — работа с БД
- **Docker Compose** — оркестрация сервисов

## Структура проекта

```
ImageHosting/
├── app/
│   ├── image_hosting_handler.py  # HTTP-маршруты и API
│   ├── base_handler.py           # Загрузка файлов, ответы
│   ├── db_manager.py             # Запросы к PostgreSQL
│   ├── QUERIES.py                # SQL-запросы
│   └── settings.py               # Пути, лимиты, расширения
├── static/                       # HTML, CSS, JS
├── images/                       # Загруженные файлы (volume)
├── logs/                         # Логи приложения и nginx
├── backups/                      # Ручные дампы PostgreSQL (backup_*.sql)
├── main.py                       # Точка входа
├── docker-compose.yml
├── Dockerfile-poetry
└── nginx.conf
```

## Быстрый старт (Docker)

### 1. Переменные окружения

Создайте файл `.env` в корне проекта:

```env
# PostgreSQL (для сервиса db в docker-compose)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=imagehosting
POSTGRES_PORT=5432

# Хост БД: для Docker — имя сервиса из compose
POSTGRES_HOST=db

# Опционально
IMAGES_LIMIT=5
STATIC_DIR=static
MEDIA_DIR=images
LOGDIR=logs
```

### 2. Создание таблицы в БД

При первом запуске таблицу `images` нужно создать вручную. Поднимите только БД:

```bash
docker compose up -d db
```

Затем выполните SQL (через `psql`, DBeaver или `docker compose exec`):

```sql
CREATE TABLE IF NOT EXISTS images (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    filename TEXT NOT NULL,
    original_name TEXT NOT NULL,
    size INTEGER NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_type TEXT NOT NULL
);
```

Тот же запрос есть в `app/QUERIES.py` (`CREATE_TABLE`). Альтернатива — раскомментировать `self.init_tables()` в `DBManager.__init__` в `app/db_manager.py` (создаст таблицу при старте приложения).

### 3. Запуск всех сервисов

```bash
docker compose up --build
```
Сервис                      |   Адрес
Веб-интерфейс (через Nginx) |   http://localhost  
Приложение напрямую         |   http://localhost:8000
PostgreSQL                  |   localhost:5432

### 4. Страницы

- `/` — главная
- `/upload`  — загрузка
- `/images`  — список изображений (пагинация: `?page=1`)
- `/gallery` — страница со всеми загруженными картинками

## Локальный запуск (без Docker)

1. Установите зависимости:

```bash
pip install -r requirements.txt
# или: poetry install
```

2. Запустите PostgreSQL и создайте таблицу `images` (см. SQL выше).

3. В `.env` укажите `POSTGRES_HOST=localhost` (или `127.0.0.1`).

4. Запустите сервер:

```bash
python main.py
```

Сервер слушает порт **8000**. Статику и папку `images/` при локальной разработке без Nginx нужно настроить отдельно или открывать только API и шаблоны через приложение.

## API


Метод     |Путь                            |Описание
`POST`    |`/api/upload`                   |Загрузка файла (`multipart/form-data`)
`GET`     |`/api/images-data/?page=N`      |Список изображений для страницы (JSON) |
`GET`     |`/api/images`                   |Имена всех файлов |
`DELETE`  |`/api/images/<filename>.<ext>`  |Удаление изображения |

Пример ответа `/api/images-data/?page=1`:

```json
{
  "images": [
    {
      "id": 1,
      "filename": "a1b2c3d4",
      "original_name": "photo.jpg",
      "size": 120,
      "upload_time": "2026-05-27 12:00:00",
      "file_type": "jpg"
    }
  ],
  "has_next": false
}
```

Публичный URL картинки: `http://<host>/images/<filename>.<file_type>` (отдаёт Nginx из каталога `images/`).

## Настройки

Параметры в `app/settings.py` и через переменные окружения:

Переменная      |По умолчанию  |Описание
`IMAGES_LIMIT`  | `5`          |Записей на страницу в списке 
`MEDIA_DIR`     | `images`     |Каталог загруженных файлов 
`STATIC_DIR`    | `static`     |Каталог шаблонов и фронтенда 
`LOGDIR`        | `logs`       |Каталог логов 

Ограничения загрузки (в коде):

- Максимальный размер файла: **5 МБ**
- Форматы: **jpg, jpeg, png, gif**

В `nginx.conf` задано `client_max_body_size 5M`.

## Логи

- `logs/server.log` — приложение Python
- `logs/access.log`, `logs/error.log` — Nginx (при монтировании volume)

## Резервное копирование (ручной бэкап БД)

1) Перейдите в корень проекта и запустите контейнер БД:

```powershell
cd D:\MyPython\PythonProject\ImageHosting
docker compose up -d db
```

2) Создайте папку под бэкапы (если уже есть — ничего страшного):

```powershell
mkdir backups 
```

3) Сделайте дамп в файл с датой/временем:
``powershell
$ts = Get-Date -Format "yyyy-MM-dd_HHmmss"
docker compose exec -T -e PGPASSWORD=postgres db pg_dump -U postgres postgres > "backups\backup_$ts.sql"
```

Где:
- `PGPASSWORD` — пароль пользователя PostgreSQL
- `-U postgres` — пользователь
- последнее `postgres` — имя базы данных (замените на значение `POSTGRES_DB` из `.env`, если у вас другое)




