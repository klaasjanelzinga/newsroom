FROM newsrooom/python-base:latest

EXPOSE 8080

COPY cron/requirements.txt cron/requirements.txt

RUN pip install --upgrade pip

COPY cron /usr/src/app/cron
COPY core_lib /usr/src/app/core_lib

RUN cd core_lib && pip install -r requirements.txt
RUN cd cron && pip install -r requirements.txt

ENV SENTRY_DSN=$SENTRY_DSN

VOLUME [ "/usr/src/app" ]

CMD ["cron/entrypoint.sh"]
