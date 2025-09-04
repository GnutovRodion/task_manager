"""
Модуль маршрутов FastAPI для работы с задачами.
Определяет REST API эндпоинты для CRUD операций над сущностью задачи:
    - получение списка всех задач
    - получение задачи по имени
    - создание новой задачи
    - обновление существующей задачи
    - обновление или создание задачи по имени
    - удаление задачи по имени
Использует вспомогательные функции из модуля task_utils для бизнес-логики.
Префикс маршрутов: /tasks.
"""

from typing import Optional

from starlette import status
from fastapi import APIRouter, Body, Response

from app.utils import tasks_utils
from app.schemas.tasks_schemas import TaskBase, TaskUpdate


router = APIRouter(prefix="/tasks")


@router.get("/", response_model=list[TaskBase])
async def get_list() -> list[TaskBase]:
    return await tasks_utils.get_all_tasks()


@router.get("/{name}", response_model=TaskBase)
async def get_one_task(name: str) -> TaskBase:
    return await tasks_utils.get_one_task(name=name)


@router.post(
    "/", response_model=TaskBase, status_code=status.HTTP_201_CREATED
)
async def create_task(task: TaskBase) -> TaskBase:
    return await tasks_utils.create_task(task=task)


@router.patch("/{name}", response_model=TaskBase)
async def update_task(
    name: str, task: Optional[TaskUpdate] = Body(None)
) -> TaskBase:
    return await tasks_utils.task_modify(name, task)


@router.put("/{name}", response_model=TaskBase)
async def update_or_create_task(
    name: str, response: Response, task: Optional[TaskBase] = Body(None)
) -> TaskBase:
    new_task, status_code = await tasks_utils.task_modify_or_create(name, task)
    response.status_code = status_code
    return new_task


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(name: str) -> Response:
    status_code = await tasks_utils.remove_task(name)
    return Response(status_code=status_code)
