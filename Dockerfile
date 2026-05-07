FROM python:3.14

ENV APP_HOME /app
WORKDIR $APP_HOME

RUN pip install poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi --no-root

COPY . .

EXPOSE 3000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]