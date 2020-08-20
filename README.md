# newsroom

## Create a deployer key for actions

- login to console.cloud.google.com
- Create a service account under IAM / Service account management.
- Grant the following roles: Service account user, Storage admin, Gcloud run admin
- Generate a .json key and rename the key to deployer.json
- Encrypt the key with `scripts/create-encrypted-file deployer.json`
- Follow the instructions from the script.

