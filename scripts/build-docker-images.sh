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

echo "Build python base-image"
(cd $script_dir/../images/python-base && docker build -t ${application}/python-base:latest .)

echo "Building app containers"
for service in unittests cron api frontend
do
  set +e
  docker pull https://docker.pkg.github.com/klaasjanelzinga/${application}/${service}:latest
  set -e
  (cd $script_dir/.. && docker build --cache-from ghcr.io/klaasjanelzinga/${application}/${service}:latest -t ${application}/${service}:$VERSION -f ${service}/Dockerfile .)
  docker tag ${application}/${service}:$VERSION ${application}/${service}:latest
  docker tag ${application}/${service}:$VERSION docker.pkg.github.com/klaasjanelzinga/${application}/${service}:$VERSION
  docker push docker.pkg.github.com/klaasjanelzinga/${application}/${service}:$VERSION
done
