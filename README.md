# Менеджер задач

# Описание проекта

CRUD приложение для управления задачами (create, get, get_list, update, delete), где модель задачи состоит из uuid, названия, описания, статусов: создано, в работе, заверешено.

# Запуск проекта через Docker-compose

1. В рабочую директорию склонируйте репозиторий: 
git clone https://github.com/GnutovRodion/task_manager.git

2. Из рабочей директории с файлом docker-compose.yml выполните команду:
docker compose up

# Стек технологий

Python | FastAPI | Alembic | Pydantic | PostgreSQL
Docker | Docker-compose | GitHub | uvicorn | asyncio

# Примеры запросов ответов

URL http://localhost:8000/tasks/
Method GET Status Code 200 OK
Response:
[
    {
        "uuid": "77c1c44053b14eaa8fe542508305ac97",
        "name": "task_1",
        "description": null,
        "status": "Создано"
    },
    {
        "uuid": "33ce1c45dcd5489781124bd2b1793dc0",
        "name": "task_2",
        "description": null,
        "status": "Создано"
    }
]


URL http://localhost:8000/tasks/task_1
Method GET Status Code 200 OK
Response: 
{
    "uuid": "77c1c44053b14eaa8fe542508305ac97",
    "name": "task_1",
    "description": null,
    "status": "Создано"
}


URL http://localhost:8000/tasks/
Request: {"name": "task_4"}
Method POST Status Code 201 Created
Response: 
{
    "uuid": "6c564c9730d04e13a5effb4306847d44",
    "name": "task_4",
    "description": null,
    "status": "Создано"
}


URL http://localhost:8000/tasks/task_4
Request: {"description": "Описание task_4"}
Method PATCH Status Code 200 OK
Response: 
{
    "uuid": null,
    "name": "task_4",
    "description": "Описание task_4",
    "status": "Создано"
}


URL http://localhost:8000/tasks/task_5
Request: 
{
    "name": "task_5",
    "status": "В работе",
    "description": "Описание task_5"
}
Method PUT Status Code 201 Created
Response:
{
    "uuid": "afc714bc11b7484a99080ca9c29d21dc",
    "name": "task_5",
    "description": "Описание task_5",
    "status": "В работе"
}


URL http://localhost:8000/tasks/task_5
Method GET Status Code 204 No Content

# Автор

Гнутов Родион 
telegram: @rodiongnutov
