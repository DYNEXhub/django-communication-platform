.PHONY: help install migrate run test clean

help:
	@echo "Django Communication Platform - Available Commands"
	@echo "=================================================="
	@echo "install       - Install dependencies"
	@echo "migrate       - Run database migrations"
	@echo "makemigrations- Create new migrations"
	@echo "createsuperuser - Create admin superuser"
	@echo "run           - Run development server"
	@echo "celery        - Run Celery worker"
	@echo "beat          - Run Celery beat scheduler"
	@echo "shell         - Open Django shell"
	@echo "test          - Run tests"
	@echo "test-cov      - Run tests with coverage"
	@echo "lint          - Run linters (black, isort, flake8)"
	@echo "format        - Format code with black and isort"
	@echo "clean         - Clean Python cache files"

install:
	pip install -r requirements/dev.txt

migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

createsuperuser:
	python manage.py createsuperuser

run:
	python manage.py runserver

celery:
	celery -A config worker --loglevel=info

beat:
	celery -A config beat --loglevel=info

shell:
	python manage.py shell

test:
	pytest

test-cov:
	pytest --cov=apps --cov-report=html --cov-report=term

lint:
	black --check .
	isort --check .
	flake8 .

format:
	black .
	isort .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name htmlcov -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
