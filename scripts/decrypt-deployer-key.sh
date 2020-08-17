#!/usr/bin/env bash

# --
# builds
set -e 

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
project_dir="$(cd "${script_dir}"/.. && pwd )"

cd "$project_dir" || (echo "project_dir not found" && exit 1)

if [ -z "$DEPLOYER_KEY" ]
then
    echo "password not set"
    exit 1
fi
gpg --quiet --batch --yes --decrypt --passphrase="$DEPLOYER_KEY" --output $project_dir/secrets/deployer.json $project_dir/etc/deployer.json.gpg
exit $?
