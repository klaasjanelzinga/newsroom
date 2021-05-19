#!/usr/bin/env bash
# Meant to run in a docker container for dev purposes

pip install -r requirements.txt
cd api
uvicorn api.__main__:app --reload --host 0.0.0.0 --port 5001
