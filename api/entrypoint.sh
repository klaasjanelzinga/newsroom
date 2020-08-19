#!/usr/bin/env bash

cd api
uvicorn api.__main__:app --reload --host 0.0.0.0 --port 8080
