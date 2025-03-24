.PHONY: build clean format lint test
IMAGE_NAME := canton-backup-utility

build:
	docker build -t $(IMAGE_NAME) .

clean:
	find . -name "*.pyc" -exec rm {} \;
	find . -name "__pycache__" -exec rm -rf {} \;
	rm -fR .pytest_cache
	rm *-users.json

format:
	poetry run isort --profile black -l 100 src/
	poetry run black -l 100 src/

lint:
	poetry run pylint src

test:
	poetry run pytest tests

all: build