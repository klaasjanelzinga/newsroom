#!/usr/bin/env bash
# ----
# --version <VERSION>
# api | cron | frontend
set -e

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
project_dir="$(cd "${script_dir}"/.. && pwd )"

services=""

while [[ $# -gt 0 ]]
do
  case "$1" in
    "--version")
      version="$2"
      shift
      ;;
    "api") services="$services api"  ;;
    "frontend") services="$services frontend"  ;;
    "cron") services="$services cron"  ;;
    *)
      echo "$1 $0 -v|--version" && exit 1
      ;;
  esac
  shift
done

[ -z "$version" ] && echo "--version is a required argument." && exit 1
[ -z "$services" ] && echo "service is a required argument." && exit 1

for service in $services
do
  [ ! -f "${project_dir}/etc/deploy-settings-$service.env" ] && echo "No settings file for $service found in the form of deploy-settings-$service.env" && exit 1

  source ${project_dir}/etc/deploy-settings-$service.env

  docker tag rss-aggregator/$service:$version gcr.io/rss-aggregator-v3/$service:$version
  docker push gcr.io/rss-aggregator-v3/$service
  gcloud --project rss-aggregator-v3 run deploy $service --platform managed --region europe-west4 $EXTRA_ARGS --image=gcr.io/rss-aggregator-v3/$service:$version
done

