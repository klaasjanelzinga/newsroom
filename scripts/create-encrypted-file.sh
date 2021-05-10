#!/usr/bin/env bash

# --
# builds

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
project_dir="$(cd "${script_dir}"/.. && pwd )"

file_to_encrypt=$1

cd "$project_dir" || (echo "project_dir not found" && exit 1)

echo "This encrypts a file and stores the file with the extension .gpg in the etc directory."

[ ! -f $file_to_encrypt ] && echo "$file_to_encrypt file not found" && exit 1

set -e
gpg --symmetric --cipher-algo AES256 $file_to_encrypt
mv $file_to_encrypt.gpg $project_dir/etc

echo "Add etc/$file_to_encrypt.gpg to git"
echo "You can delete $file_to_encrypt"
