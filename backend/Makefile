    .PHONY: install run lint format test coverage docker-build docker-run

    install:
	pip install -U pip && pip install -r requirements-dev.txt

    run:
	uvicorn app.main:app --reload

    lint:
	ruff check .
	mypy app

    format:
	ruff format .

    test:
	pytest -q --cov=app --cov-report=term-missing

    coverage:
	pytest --cov=app --cov-report=xml

    docker-build:
	docker build -t videolingo-backend:dev .

    docker-run:
	docker run --rm -p 8000:8000 --env-file .env videolingo-backend:dev
