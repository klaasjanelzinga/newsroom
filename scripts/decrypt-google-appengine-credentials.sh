#!/usr/bin/env bash

# --
# builds

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
project_dir="$(cd "${script_dir}"/.. && pwd )"

cd "$project_dir" || (echo "project_dir not found" && exit 1)

[ ! -f $project_dir/etc/google-appengine-credentials.json.gpg ] && echo "Input encrypted file not found" && exit 1
if [ -z "$GOOGLE_APP_ENGINE_KEY" ]
then
    echo -n Password: 
    read -s GOOGLE_APP_ENGINE_KEY
    echo
fi

mkdir -p $project_dir/secrets
if [ -z "$GOOGLE_APP_ENGINE_KEY" ]
then
    echo "password not set"
    exit 1
fi
gpg --quiet --batch --yes --decrypt --passphrase="$GOOGLE_APP_ENGINE_KEY" --output $project_dir/secrets/google-appengine-credentials.json $project_dir/etc/google-appengine-credentials.json.gpg

echo "Credentials created in secrets/google-appengine-credentials.json"
