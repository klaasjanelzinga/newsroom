#!/usr/bin/env bash

# --
# builds

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
project_dir="$(cd "${script_dir}"/.. && pwd )"

file_to_decrypt=$1
target_name=$2

cd "$project_dir" || (echo "project_dir not found" && exit 1)

echo "This decrypts a file and stores the file without the extension .gpg in the project directory."

[ ! -f $file_to_decrypt ] && echo "$file_to_decrypt file not found" && exit 1
[ -z "$target_name" ] && echo  "$target_name exists. Operation cancelled." && exit 2
[ -f $target_name ] && echo  "$target_name exists. Operation cancelled" && exit 2

set -e
gpg --decrypt $file_to_decrypt > $target_name

