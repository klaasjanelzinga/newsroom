#!/usr/bin/env bash

cd cron
uvicorn cron.__main__:app --reload --host 0.0.0.0 --port 8080
