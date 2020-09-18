FROM python:3.8-slim

RUN apt-get update && apt-get install -y gcc locales procps make
RUN echo "nl_NL.UTF-8 UTF-8" >> /etc/locale.gen
RUN locale-gen

EXPOSE 8080

ENV ENVIRONMENT=PRODUCTION
ENV PYTHONDONTWRITEBYTECODE 3

WORKDIR /usr/src/app
COPY requirements.txt ./requirements.txt
COPY Makefile ./Makefile
COPY pyproject.toml ./pyproject.toml

COPY cron /usr/src/app/cron
COPY core_lib /usr/src/app/core_lib
COPY api /usr/src/app/api
COPY unittests /usr/src/app/unittests

RUN make requirements

VOLUME [ "/usr/src/app" ]

CMD ["unittests/entrypoint.sh"]
