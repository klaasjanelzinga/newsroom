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
for service in cron api frontend
do
  ghcrio_image_name=ghcr.io/klaasjanelzinga/${application}/${service}
  set +e
  docker pull ${ghcrio_image_name}:latest
  set -e
  (cd $script_dir/.. && docker build --cache-from ${ghcrio_image_name}:latest -t ${ghcrio_image_name}:$VERSION -f ${service}/Dockerfile .)
  docker tag ${ghcrio_image_name}:$VERSION ${ghcrio_image_name}:latest
  docker push ${ghcrio_image_name}:$VERSION
  docker push ${ghcrio_image_name}:latest
done

