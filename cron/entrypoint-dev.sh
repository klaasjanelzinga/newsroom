#!/usr/bin/env bash
# Meant to run in a docker container for dev purposes

pip install -r requirements.txt
cd cron
uvicorn cron.__main__:app --reload --reload-dir .. --host 0.0.0.0 --port 5002
