#!/usr/bin/env bash
# -----
# -v VERSION
set -e

VERSION="BETA"

while [[ $# -gt 0 ]]
do
  case "$1" in
    "--version")
      VERSION="$2"
      shift
      ;;
    *)
      echo "$1 $0 -v|--version" && exit 1
      ;;
  esac
  shift
done

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
application=newsrooom

echo "Building app containers"
for service in unittests cron api frontend
do
  set +e
  docker pull gcr.io/newsroom-v1/${service}:latest
  set -e
  (cd $script_dir/.. && docker build --cache-from gcr.io/newsroom-v1/${service}:latest -t ${application}/${service}:$VERSION -f ${service}/Dockerfile .)
  docker tag ${application}/${service}:$VERSION ${application}/${service}:latest
done
