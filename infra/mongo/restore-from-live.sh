#!/usr/bin/env bash

mongorestore \
  --uri="mongodb://${MONGO_USER}:${MONGO_PASS}@localhost:${MONGO_PORT}/newsroom" \
  --nsInclude="newsroom.*" \
  --archive=/backups/newsroom-20210611.archive
