FROM python:3.8-slim

RUN apt-get update && apt-get install -y gcc locales procps make
RUN echo "nl_NL.UTF-8 UTF-8" >> /etc/locale.gen
RUN locale-gen

EXPOSE 8080

ENV ENVIRONMENT=PRODUCTION
ENV PYTHONDONTWRITEBYTECODE 3

RUN pip install --upgrade pip

WORKDIR /usr/src/app

