"""
Модуль с Pydantic мщделями для работы с задачами.
Содержит базовую модель задачи (TaskBase), модель для создания
задачи (TaskCreate) и модель для обновления задачи (TaskCreate).
Модели обеспечивают валидацию данных, ограничения длины полей,
дефолтные значения, конвертацию UUID в строковый формат.
"""

from typing import Optional

from pydantic import BaseModel, UUID4, field_validator, Field, ConfigDict

from app.models.tasks_model import TaskStatus


class TaskBase(BaseModel):
    """Модель задачи."""
    uuid: Optional[UUID4] = None
    name: str = Field(..., min_length=1, max_length=256)
    description: Optional[str] = None
    status: TaskStatus = Field(default=TaskStatus.CREATED)

    @field_validator("uuid")
    def convert_uuid_to_hex(cls, value):
        """Конвертирует UUID в строку."""
        if value is not None:
            return value.hex

    model_config = ConfigDict(
        populate_by_name=True, extra="forbid"
    )


class TaskUpdate(BaseModel):
    """Модель для изменения задачи."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None

    model_config = ConfigDict(extra="forbid")
