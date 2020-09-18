FROM newsrooom/python-base:latest

COPY requirements.txt ./requirements.txt
COPY Makefile ./Makefile
COPY pyproject.toml ./pyproject.toml
COPY mypy.ini ./mypy.ini
COPY pylintrc ./pylintrc
COPY .isort.cfg ./.isort.cfg
COPY .flake8 ./.flake8


COPY cron /usr/src/app/cron
COPY core_lib /usr/src/app/core_lib
COPY api /usr/src/app/api
COPY unittests /usr/src/app/unittests

RUN make requirements

VOLUME [ "/usr/src/app" ]

CMD ["unittests/entrypoint.sh"]
