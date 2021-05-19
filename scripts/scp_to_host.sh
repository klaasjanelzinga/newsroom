#!/usr/bin/env bash

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
project_dir="$(cd "${script_dir}"/.. && pwd )"

target_host=test.n-kj.nl

scp $project_dir/etc/production.env scp://$target_host//usr/newsroom/etc/production.env
scp $project_dir/docker-compose-live.yml scp://$target_host//usr/newsroom/
scp $project_dir/Makefile scp://$target_host//usr/newsroom/
