#!/usr/bin/env bash

cd cron
uvicorn cron.__main__:app --host 0.0.0.0 --port 5002
