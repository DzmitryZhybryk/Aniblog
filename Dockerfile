FROM python:3.10
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /code
COPY ./backend/authentication/poetry.lock ./backend/authentication/pyproject.toml ./
COPY ./backend/authentication/app /code/app
RUN pip install --upgdare pip
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry lock
RUN poetry install --no-interaction --no-ansi