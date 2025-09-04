FROM python:3.12

RUN pip install --no-cache-dir poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* alembic.ini ./

COPY migrations/ ./migrations

COPY /app ./app

RUN poetry install --no-cache 

ENV PYTHONPATH=/app/app

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
