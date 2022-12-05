FROM python:3.10
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /code
COPY poetry.lock ./pyproject.toml ./
COPY app /code/app
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry lock
RUN poetry install --no-interaction --no-ansi