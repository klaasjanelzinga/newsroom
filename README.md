# newsroom

## Create a ci-test account

- login to [console](https://console.cloud.google.com)
- create a new project in google-cloud.
- Add a datastore, select Cloud Firestore in Datastore mode, location: europe-west3.
- create a service account.
- grant owner role.
- create a key.
- rename the key file to google-appengine-credentials.json
- Encrypt the key with `scripts/create-encrypted-file.sh google-appengine-credentials.json`
- Follow the instructions from the script.
- Run `scripts/decrypt-google-appengine-credentials.sh`. This will create the unencrypted file 
  `secrets/google-appengine-credentials.json`. 
- Set the location of this file as an environment variable to run the application locally and connect to this test project: `GOOGLE_APPLICATION_CREDENTIALS=<unencryted-google-appengine-credentials.json file location>` 

## Create a deployer key for actions

- login to [console](https://console.cloud.google.com)
- Create a service account under IAM / Service account management.
- Grant the following roles: Service account user, Storage admin, Gcloud run admin
- Generate a .json key and rename the key to deployer.json
- Encrypt the key with `scripts/create-encrypted-file deployer.json`
- Follow the instructions from the script.



[console]: https://console.cloud.google.com