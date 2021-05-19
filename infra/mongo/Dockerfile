FROM mongo:4.4-bionic

COPY init-mongo.sh /docker-entrypoint-initdb.d/
COPY mongo.conf /etc/

VOLUME /data/db
