"""
Модуль с тестами для API эндпоинтов управления задачами в FastAPI-приложении.
Включает тесты для операций CRUD, а также проверки на невалидные
данные и edge-кейсы.
Тесты используют pytest с фикстурами для изоляции
(временная БД, сессии, клиент).
"""

import pytest

from app.models.tasks_model import tasks_table, TaskStatus


def test_get_all_tasks(client, db_session):
    """Тестирование получения всех задач."""
    task_name = "test_get_name_task"
    test_task = tasks_table.insert().values(
        name=task_name, status=TaskStatus.CREATED
    )
    db_session.execute(test_task)
    db_session.commit()
    response = client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["name"] == task_name


def test_get_one_task(client, db_session):
    """Тестирование успешного получения задачи по имени."""
    task_name = "test_get_name_task"
    test_task = tasks_table.insert().values(
        name=task_name, status=TaskStatus.CREATED
    )
    db_session.execute(test_task)
    db_session.commit()
    response = client.get(f"/tasks/{task_name}")
    assert response.status_code == 200
    tasks = response.json()
    assert tasks["name"] == task_name


def test_get_lost_task(client, temp_db):
    """Тестирование получения несуществующей задачи."""
    response = client.get("/tasks/lost_task")
    assert response.status_code == 404


@pytest.mark.parametrize("task_data_create, case_name_create", [
    ({
        "name": "task_example_1"
    },
        "minimal_config"
    ),
    ({
        "name": "task_example_2",
        "status": "Завершено"
    },
        "with_status"
    ),
    ({
        "name": "task_example_3",
        "description": "description task_3"
    },
        "with_description"
    ),
    ({
        "name": "task_example_4",
        "status": "В работе",
        "description": "description task_4"
    },
        "maximum_config"
    )
])
def test_create_task(
    client, temp_db, db_session, task_data_create, case_name_create
):
    """Тестирование успешного создания задачи с разными входными данными."""
    response = client.post("/tasks/", json=task_data_create)
    assert response.status_code == 201
    task = response.json()
    assert task["name"] == task_data_create["name"]
    if "description" in task_data_create:
        assert task["description"] == task_data_create["description"]
    else:
        assert task["description"] is None
    if "status" in task_data_create:
        assert task["status"] == task_data_create["status"]
    else:
        assert task["status"] == "Создано"


def test_create_bad_task(client, db_session, bad_params):
    """Тестирование создания задачи с невалидными данными."""
    response = client.post("/tasks", json={})
    assert response.status_code == 422
    for param in bad_params:
        response = client.post("/tasks", json=param)
        response.status_code == 422
        if "name" in param[0] and param[0]["name"]:
            query = tasks_table.select().where(
                tasks_table.c.name == param[0]["name"]
            )
            result = db_session.execute(query).fetchone()
            assert result is None


def test_create_existing_task(client, db_session):
    """Тестирование повторного создания задачи."""
    task_name = "existing_task"
    db_session.execute(tasks_table.insert().values(
        name=task_name, status=TaskStatus.CREATED
    ))
    db_session.commit()
    response = client.post("/tasks", json={"name": task_name})
    assert response.status_code == 400
    rows = db_session.execute(tasks_table.select().where(
        tasks_table.c.name == task_name)).fetchall()
    assert len(rows) == 1


@pytest.mark.parametrize("task_data_patch, case_name_patch", [
    ({}, "minimal_config"),
    ({
        "name": "task_example_5"
    },
        "only_name"
    ),
    ({
        "description": "new_description"
    },
        "only_description"
    ),
    ({
        "status": "Создано"
    },
        "only_status"
    ),
    ({
        "name": "task_example_6",
        "description": "description_task_example_6"
    },
        "name_and_description"
    ),
    ({
        "description": "new_description_task_example_6",
        "status": "Завершено"
    },
        "description_and_status"
    ),
    ({
        "name": "task_example_7",
        "description": "last_description",
        "status": "В работе"
    },
        "maximum_config"
    )
])
def test_patch_task(
    client, temp_db, db_session, task_data_patch, case_name_patch
):
    """Тестирование частичного изменения задачи."""
    task_name = f"task_{case_name_patch}"
    test_task = tasks_table.insert().values(
        name=task_name, status=TaskStatus.COMPLETED
    ).returning(
        tasks_table.c.name,
        tasks_table.c.description,
        tasks_table.c.status
    )
    result = db_session.execute(test_task)
    db_session.commit()
    initial_task = result.mappings().first()
    response = client.patch(f"/tasks/{task_name}", json=task_data_patch)
    assert response.status_code == 200
    task = response.json()
    if "name" in task_data_patch:
        assert task["name"] == task_data_patch["name"]
    else:
        assert task["name"] == initial_task["name"]
    if "description" in task_data_patch:
        assert task["description"] == task_data_patch["description"]
    else:
        assert task["description"] == initial_task["description"]
    if "status" in task_data_patch:
        assert task["status"] == task_data_patch["status"]
    else:
        assert task["status"] == initial_task["status"].value


def test_patch_bad_task(client, db_session, bad_params):
    """Тестирование частичного изменения задачи с невалидными данными."""
    task_name = "bad_task_patch"
    task = tasks_table.insert().values(
        name=task_name, status=TaskStatus.CREATED.name
    )
    db_session.execute(task)
    db_session.commit()
    original_task = db_session.execute(tasks_table.select().where(
        tasks_table.c.name == task_name)).fetchone()
    for param in bad_params:
        response = client.patch(f"tasks/{task_name}", json=param)
        assert response.status_code == 422
        if param[0]["name"]:
            update_task = db_session.execute(
                tasks_table.select().where(
                    tasks_table.c.name == param[0]["name"])).fetchone()
            assert update_task is None
            no_update_task = db_session.execute(
                tasks_table.select().where(
                    tasks_table.c.name == task_name)).fetchone()
            assert original_task == no_update_task


def test_patch_lost_task(client, temp_db):
    """Тестирование частичного изменения несуществующей задачи."""
    response = client.patch("/tasks/lost_patch_task")
    assert response.status_code == 404


def test_put_task(client, temp_db, db_session):
    """Тестирование успешного изменения или создания задачи."""
    task_name = "test_put_task"
    test_task = tasks_table.insert().values(
        name=task_name, status=TaskStatus.IN_PROGRESS
    )
    db_session.execute(test_task)
    db_session.commit()
    update_task = {
        "name": "put_task_name",
        "status": "Завершено",
        "description": "Новое описание задачи."
    }
    new_task = {
        "name": "new_put_task",
        "status": "В работе",
        "description": "Описание новой задачи."
    }
    resp_if_not_task_and_not_body = client.put("/tasks/put_task")
    assert resp_if_not_task_and_not_body.status_code == 201
    put_task = resp_if_not_task_and_not_body.json()
    assert put_task["name"] == "put_task"
    assert put_task["description"] is None
    assert put_task["status"] == "Создано"
    resp_if_not_task_and_body = client.put(
        "/tasks/new_put_task", json=new_task
    )
    assert resp_if_not_task_and_body.status_code == 201
    new_put_task = resp_if_not_task_and_body.json()
    assert new_put_task["name"] == new_task["name"]
    assert new_put_task["description"] == new_task["description"]
    assert new_put_task["status"] == new_task['status']
    resp_if_task_not_body = client.put(f'/tasks/{task_name}')
    assert resp_if_task_not_body.status_code == 200
    original_task_resp = resp_if_task_not_body.json()
    result = db_session.execute(
        tasks_table.select().where(tasks_table.c.name == task_name)
    )
    original_task = result.fetchone()
    assert original_task_resp["name"] == original_task[1]
    assert original_task_resp["description"] == original_task[2]
    assert original_task_resp["status"] == original_task[3].value
    resp_if_task_and_body = client.put(f"tasks/{task_name}", json=update_task)
    assert resp_if_task_and_body.status_code == 200
    modify_task = resp_if_task_and_body.json()
    assert modify_task["name"] == update_task["name"]
    assert modify_task["description"] == update_task["description"]
    assert modify_task["status"] == update_task["status"]


def test_put_bad_task(client, db_session, bad_params):
    """Тестирование изменения или создания задачи с невалидными данными."""
    for param in bad_params:
        response = client.put("/tasks/task_bad_put", json=param)
        assert response.status_code == 422
        if param[0]["name"]:
            bad_task = db_session.execute(
                tasks_table.select().where(
                    tasks_table.c.name == param[0]["name"])).fetchone()
            assert bad_task is None
    task_name = "bad_task_put"
    db_session.execute(
        tasks_table.insert().values(
            name=task_name, status=TaskStatus.CREATED.name))
    db_session.commit()
    original_task = db_session.execute(
        tasks_table.select().where(
            tasks_table.c.name == task_name)).fetchone()
    for param in bad_params:
        response = client.put(f"/tasks/{task_name}", json=param)
        assert response.status_code == 422
        no_update_task = db_session.execute(
            tasks_table.select().where(
                tasks_table.c.name == task_name)).fetchone()
        assert original_task == no_update_task


def test_delete_task(client, temp_db, db_session):
    """Тестирование удаления задачи."""
    task_name = "deleted_task"
    task = tasks_table.insert().values(
        name=task_name, status=TaskStatus.CREATED.name
    )
    db_session.execute(task)
    db_session.commit()
    response = client.delete(f"/tasks/{task_name}")
    assert response.status_code == 204
    deleted_task = db_session.execute(
        tasks_table.select().where(tasks_table.c.name == task_name)
    ).fetchone()
    assert deleted_task is None


def test_delete_lost_task(client, temp_db):
    """Тестирование удаления несуществующей задачи."""
    response = client.delete("/tasks/task_lost_delete")
    assert response.status_code == 404
