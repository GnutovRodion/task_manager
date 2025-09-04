"""
Модуль с определением таблицы задач для Alembic-миграций.
Содержит схему таблицы 'tasks' с колонками для UUID, названия,
описания и статуса (Создано, В работе, Завершено).
Используется для создания/обновления структуры базы данных в PostgreSQL.
"""

import enum

from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Table, Column, MetaData, String, Text, text


metadata = MetaData()


class TaskStatus(enum.Enum):
    CREATED = "Создано"
    IN_PROGRESS = "В работе"
    COMPLETED = "Завершено"


tasks_table = Table(
    "tasks",
    metadata,
    Column(
        "uuid",
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    ),
    Column("name", String(256), nullable=False, index=True),
    Column("description", Text),
    Column(
        "status",
        Enum(TaskStatus, name="taskstatus", create_type=False),
        nullable=False,
        default=TaskStatus.CREATED.value
    )
)
