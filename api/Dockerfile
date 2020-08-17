FROM python:3.8-slim

RUN apt-get update && apt-get install -y gcc locales procps make
RUN echo "nl_NL.UTF-8 UTF-8" >> /etc/locale.gen
RUN locale-gen

EXPOSE 8080

ENV ENVIRONMENT=PRODUCTION
ENV PYTHONDONTWRITEBYTECODE 3

WORKDIR /usr/src/app
COPY api/requirements.txt api/requirements.txt

RUN pip install --upgrade pip

COPY api /usr/src/app/api
COPY core_lib /usr/src/app/core_lib

RUN cd core_lib && pip install -r requirements.txt
RUN cd api && pip install -r requirements.txt

VOLUME [ "/usr/src/app" ]

CMD ["api/entrypoint.sh"]