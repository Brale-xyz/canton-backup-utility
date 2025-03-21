.PHONY: format test lint clean
format:
	poetry run isort --profile black -l 100 src/
	poetry run black -l 100 src/

test:
	poetry run pytest tests

lint:
	poetry run pylint src

clean:
	find . -name "*.pyc" -exec rm {} \;
	find . -name "__pycache__" -exec rm -rf {} \;
	rm -fR .pytest_cache
	rm *-users.json

all: lint 
