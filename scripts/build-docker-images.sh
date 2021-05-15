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
  ghcrio_image_name=ghcr.io/klaasjanelzinga/${application}/${service}
  set +e
  docker pull ${ghcrio_image_name}:latest
  set -e
  (cd $script_dir/.. && docker build --cache-from ${ghcrio_image_name}:latest -t ${application}/${service}:$VERSION -f ${service}/Dockerfile .)
  docker tag ${application}/${service}:$VERSION ${application}/${service}:latest
  docker tag ${application}/${service}:$VERSION ${ghcrio_image_name}:$VERSION
  docker push ${ghcrio_image_name}:$VERSION
done

echo "Building infra containers"
infra_dir=${script_dir}/../infra
(cd $infra_dir/nginx && docker build -t ghcr.io/klaasjanelzinga/${application}/nginx:$VERSION .
(cd $infra_dir/mongo && docker build -t ghcr.io/klaasjanelzinga/${application}/mongo:$VERSION .

docker push ghcr.io/klaasjanelzinga/${application}/nginx
docker push ghcr.io/klaasjanelzinga/${application}/mongo
