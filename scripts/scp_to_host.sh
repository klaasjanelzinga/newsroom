#!/usr/bin/env bash

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
project_dir="$(cd "${script_dir}"/.. && pwd )"

target_host=94.130.214.19

scp $project_dir/etc/production.env scp://root@$target_host//usr/newsroom/etc/production.env
scp $project_dir/docker-compose-live.yml scp://root@$target_host//usr/newsroom/
