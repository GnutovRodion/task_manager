"""
Модуль бизнес-логики для операций CRUD с задачами.
Содержит асинхронные функции для работы с задачами в базе данных:
    - получение списка всех задач
    - получение задачи по имени
    - создание новой задачи с проверкой на дубликаты
    - обновление существующей задачи
    - обновление или создание задачи, если такой еще не существует
    - удаление задачи
Использует Singleton-класс для подключения к БД, модели из tasks_model
и схемы из tasks_schemas для валидации данных.
Все функции обрабатывают ошибки с помощью HTTPException и возвращают
коды статуса.
"""

from typing import Optional

from fastapi import HTTPException
from starlette import status

from app.db import DatabaseSingleton
from app.models.tasks_model import tasks_table
from app.schemas.tasks_schemas import TaskBase, TaskUpdate
from models.tasks_model import TaskStatus


db = DatabaseSingleton()


async def get_task_by_name(name: str) -> TaskBase | None:
    """Вспомогательная функция для получения задачи из БД по имени."""
    task = await db.fetch_one(
        tasks_table.select().where(tasks_table.c.name == name)
    )
    if task:
        return TaskBase(**task)
    return None


async def get_all_tasks() -> list[TaskBase]:
    """Получает все задачи."""
    query = tasks_table.select()
    rows = await db.fetch_all(query)
    return [TaskBase(**row) for row in rows]


async def get_one_task(name: str) -> TaskBase:
    """Выполняет поиск задачи по названию."""
    query = tasks_table.select().where(tasks_table.c.name == name)
    result = await db.fetch_one(query)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача {name} не найдена."
        )
    return TaskBase(**result)


async def create_task(task: TaskBase) -> TaskBase:
    """Создает новую задачу."""
    db_task = await get_task_by_name(task.name)
    if db_task is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Задача {task.name} уже существует."
        )
    query = tasks_table.insert().values(
        name=task.name,
        description=task.description,
        status=task.status.name
    )
    await db.execute(query)
    return await get_task_by_name(task.name)


async def task_modify(name: str, task: TaskUpdate) -> TaskBase:
    """Изменяет задачу."""
    db_task = await get_task_by_name(name)
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача {name} не найдена."
        )
    if not task or not task.model_dump(exclude_unset=True):
        return db_task
    data_to_change = {
        k: v.name if k == "status" else v
        for k, v in task.model_dump(exclude_unset=True).items()
        if v is not None
    }
    query = (
        tasks_table.update()
        .where(tasks_table.c.name == name)
        .values(**data_to_change)
        .returning(
            tasks_table.c.name,
            tasks_table.c.description,
            tasks_table.c.status
        )
    )
    modify = await db.fetch_one(query)
    return TaskBase(**modify)


async def task_modify_or_create(
    name: str, task: Optional[TaskBase] = None
) -> tuple[TaskBase, int]:
    """Изменяет или создает (если такой не существует) задачу."""
    db_task = await get_task_by_name(name)
    if task is not None:
        data = {
            k: v.name if k == "status" else v
            for k, v in task.model_dump(exclude_unset=True).items()
            if v is not None
        }
    else:
        data = {"name": name, "status": TaskStatus.CREATED.name}
    if db_task is None:
        query = tasks_table.insert().values(**data)
        await db.execute(query)
        query_get_task = tasks_table.select().where(
            tasks_table.c.name == name
        )
        row = await db.fetch_one(query_get_task)
        return TaskBase(**row), status.HTTP_201_CREATED
    else:
        if task is None:
            return db_task.model_dump(), status.HTTP_200_OK
        query = (
            tasks_table.update()
            .where(tasks_table.c.name == name)
            .values(**data)
            .returning(
                tasks_table.c.name,
                tasks_table.c.description,
                tasks_table.c.status
            )
        )
        modify = await db.fetch_one(query)
        return TaskBase(**modify), status.HTTP_200_OK


async def remove_task(name: str) -> int:
    """Удаляет задачу."""
    query = (
        tasks_table.delete()
        .where(tasks_table.c.name == name)
        .returning(tasks_table.c.name)
    )
    deleted = await db.fetch_one(query)
    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача {name} не найдена."
        )
    return status.HTTP_204_NO_CONTENT
