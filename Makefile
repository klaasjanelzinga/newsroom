# -------------------------------------------------------
# Commands for starting and stopping the application
init-data-directory:
	mkdir -p infra/data/redis infra/data/mongodb

build:
	docker-compose --env-file etc/dev.env build

up: init-data-directory
	docker-compose --env-file etc/dev.env up

up-infra: init-data-directory
	docker-compose --env-file etc/dev.env up mongo mongo-express

up-frontend: init-data-directory
	docker-compose --env-file etc/dev.env up frontend

down: init-data-directory
	docker-compose --env-file etc/dev.env down

logs:
	docker-compose logs -f

restore-live-backup-to-mongo:
	docker-compose --env-file etc/dev.env exec mongo /restore-from-live.sh

restart-frontend:
	docker-compose restart frontend

run-tests-in-docker:
	(cd images/python-base && docker build -t newsrooom/python-base:latest .)
	docker-compose --env-file secrets/test.env -f docker-compose-test.yml up --remove-orphans --exit-code-from unittests
	docker-compose --env-file secrets/test.env -f docker-compose-test.yml down --remove-orphans

# -------------------------------------------------------
# Dependency management
requirements:
	(pip install -r requirements.txt)
	(cd api && pip install -r requirements.txt)
	(cd cron && pip install -r requirements.txt)
	(cd core_lib && pip install -r requirements.txt)
	(cd unittests && pip install -r requirements.txt)

upgrade-requirements:
	(pip-compile --upgrade)
	(cd api && pip-compile --upgrade)
	(cd cron && pip-compile --upgrade)
	(cd core_lib && pip-compile --upgrade)
	(cd unittests && pip-compile --upgrade)

# -------------------------------------------------------
# Devops
devops-mongo-express:
	ssh -L 5901:127.0.0.1:5901 test.n-kj.nl

live-up:
	docker-compose -f docker-compose-live.yml --env-file etc/production.env pull
	docker-compose -f docker-compose-live.yml --env-file etc/production.env down
	docker-compose -f docker-compose-live.yml --env-file etc/production.env up --detach
	docker rmi $(docker images -q)

live-down:
	docker-compose -f docker-compose-live.yml --env-file etc/production.env down

scp-to-host:
	scp Makefile docker-compose-live.yml scp://test.n-kj.nl//usr/newsroom
	scp -r etc/production.env etc/production.env scp://test.n-kj.nl//usr/newsroom/etc

# -------------------------------------------------------
# Test application
cron-refresh-feeds:
	curl localhost:5002/maintenance/refresh-feeds

cron-delete-read-items:
	curl localhost:5002/maintenance/delete-read-items

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

