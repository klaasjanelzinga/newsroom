#!/usr/bin/env bash

# --
# builds

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
project_dir="$(cd "${script_dir}"/.. && pwd )"

file_to_encrypt=$1

cd "$project_dir" || (echo "project_dir not found" && exit 1)

echo "A json token file is required. This can be created in the google app engine."
echo "Go to project, API & Services -> Credentials (of any but the live gae project)."
echo "Create credentials, Service Account Key"
echo "Give it a meaningfull name, and at least access to datastore, logging"
echo "Save the json token and pass to this script"

[ ! -f $file_to_encrypt ] && echo "JSON token file $file_to_encrypt file not found" && exit 1

set -e
gpg --symmetric --cipher-algo AES256 $file_to_encrypt
mv $file_to_encrypt.gpg $project_dir/etc

echo "Add etc/$file_to_encrypt.gpg to git"
echo "Add secret to github as environment variable GOOGLE_APP_ENGINE_KEY"
echo "You can delete $file_to_encrypt"
