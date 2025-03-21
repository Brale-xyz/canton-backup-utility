FROM python:3.13-slim-bookworm

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # Poetry's configuration:
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_VERSION=2.1.1

RUN apt update -y && apt install --no-install-recommends -y curl
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN mkdir -p /app

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml README.md /app/
# Install only the dependencies
RUN ["poetry", "install", "--no-interaction", "--no-ansi", "--no-root"]

# # Creating folders, and files for a project:
COPY . /app
# Install the project
RUN ["poetry", "install", "--no-interaction", "--no-ansi"]

ENTRYPOINT ["/app/util.sh"]
