# -------------------------------------------------------
# Commands for starting and stopping the application
init-data-directory:
	mkdir -p data/redis data/mongodb

up-build: init-data-directory
	docker-compose up --build --detach

up: init-data-directory
	docker-compose up --detach

down: init-data-directory
	docker-compose down

logs:
	docker-compose logs -f

restart-frontend:
	docker-compose restart frontend

# -------------------------------------------------------
# Dependency management
requirements:
	(pip install -r requirements.txt)
	(cd api && pip install -r requirements.txt)
	(cd cron && pip install -r requirements.txt)
	(cd core_lib && pip install -r requirements.txt)
	(cd unittests && pip install -r requirements.txt)

upgrade-requirements:
	(pip-compile --upgrade requirements.in > requirements.txt)
	(cd api && pip-compile --upgrade requirements.in > requirements.txt)
	(cd cron && pip-compile --upgrade requirements.in > requirements.txt)
	(cd core_lib && pip-compile --upgrade requirements.in > requirements.txt)
	(cd unittests && pip-compile --upgrade requirements.in > requirements.txt)

# -------------------------------------------------------
# Code maintenance
black:
	black core_lib/core_lib api/api cron/cron unittests/tests

black-check:
	black --check core_lib/core_lib api/api cron/cron unittests/tests

pylint:
	pylint core_lib/core_lib api/api cron/cron

mypy:
	(cd core_lib && mypy --config-file ../mypy.ini -p core_lib)
	(cd api && mypy --config-file ../mypy.ini -p api)
	(cd cron && mypy --config-file ../mypy.ini  -p cron)

tslint:
	docker-compose run frontend npm run lint

isort:
	isort -rc core_lib/core_lib api/api cron/cron

flakes: black isort flake8 mypy pylint tslint

flakes-check: black-check mypy flake8

flake8:
	flake8 core_lib/core_lib

tests:
	(cd unittests && export unit_tests=1 && pytest --cov core_lib --cov api --cov cron --cov-report=html tests)

build-docker-images:
	scripts/build-docker-images.sh

es-lint:
	docker-compose run --entrypoint "npm run lint" frontend

before-commit: flakes tests build-docker-images integration-tests

cron-refresh-feeds:
	curl localhost:9090/maintenance/refresh-feeds

cron-delete-read-items:
	curl localhost:9090/maintenance/delete-read-items
