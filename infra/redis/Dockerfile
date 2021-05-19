FROM redislabs/redisearch:6.2

COPY redis.conf /usr/local/etc/redis/redis.conf
VOLUME /data

CMD [ "redis-server", "/usr/local/etc/redis/redis.conf" ]