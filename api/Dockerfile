FROM newsrooom/python-base:latest

EXPOSE 8080

COPY api/requirements.txt api/requirements.txt

RUN pip install --upgrade pip

COPY api /usr/src/app/api
COPY core_lib /usr/src/app/core_lib

RUN cd core_lib && pip install -r requirements.txt
RUN cd api && pip install -r requirements.txt

ENV TOKEN_SECRET=$TOKEN_SECRET

VOLUME [ "/usr/src/app" ]

CMD ["api/entrypoint.sh"]