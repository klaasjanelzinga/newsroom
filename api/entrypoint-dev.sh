#!/usr/bin/env bash
# Meant to run in a docker container for dev purposes

pip install -r requirements.txt
cd api
watchmedo auto-restart --recursive --pattern=*.py --directory=.. -- python -m api
