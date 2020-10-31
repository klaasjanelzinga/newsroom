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

outdated:
	pip list --outdated

flakes: black flake8 outdated mypy pylint tslint

flakes-check: black-check mypy outdated flake8

flake8:
	flake8 core_lib/core_lib

tests:
	(cd unittests && export unit_tests=1 && pytest --cov core_lib --cov api --cov cron --cov-report=html tests)

dev-requirements:
	pip install -r requirements.txt

requirements: dev-requirements
	pip install --upgrade pip
	(cd api && pip install --upgrade -r requirements.txt)
	(cd cron && pip install --upgrade -r requirements.txt)
	(cd core_lib && pip install --upgrade -r requirements.txt)
	(cd unittests && pip install --upgrade -r requirements.txt)


build-docker-images:
	scripts/build-docker-images.sh

integration-tests:
	(cd integration && docker-compose up --exit-code-from integration_test integration_test)

integration-tests-down:
	(cd integration && docker-compose down)


up: 
	docker-compose up --build

before-commit: flakes tests build-docker-images integration-tests

cron-refresh-rss-feeds:
	curl localhost:9090/maintenance/refresh-rss-feeds

cron-refresh-atom-feeds:
	curl localhost:9090/maintenance/refresh-atom-feeds

cron-refresh-html-feeds:
	curl localhost:9090/maintenance/refresh-html-feeds

cron-delete-read-items:
	curl localhost:9090/maintenance/delete-read-items
