#!/usr/bin/env bash

echo "Log on to console and create a new project."

PROJECT_ID=rss-aggregator-v3
CRON_URL=https://cron-ntapdiwuga-ez.a.run.app


# Enable Cloud Run in console.
# Add datastore:
# You selected Cloud Firestore in Datastore mode. Now choose a database location. (europe-west3)
# Add indexes: gcloud datastore indexes create index.yaml
# scripts/build-docker-images.sh
#
# docker tag rss-aggregator/api:BETA gcr.io/rss-aggregator-v3/api:BETA
# docker push gcr.io/rss-aggregator-v3/api
# gcloud --project rss-aggregator-v3 run deploy api --platform managed --region europe-west4 --image=gcr.io/rss-aggregator-v3/api:BETA --allow-unauthenticated --command=python --args=api.py
#
# goto iam -> service account Add service account:
# name deployer
# Roles gcloud run admin, service account user


gcloud components update
gcloud config set run/platform managed
gcloud config set run/region europe-west4
gcloud auth configure-docker
gcloud components install docker-credential-gcr

# Enable cloud scheduler, service account with permissions on cron service.
gcloud services enable cloudscheduler.googleapis.com
gcloud iam service-accounts create rss-aggregator-scheduler --display-name "RSS Aggregator scheduler"
gcloud run services add-iam-policy-binding cron \
   --member=serviceAccount:rss-aggregator-scheduler@${PROJECT_ID}.iam.gserviceaccount.com \
   --role=roles/run.invoker

# Schedule two jobs.
gcloud beta scheduler jobs create http fetch-job --schedule "every 7 hours" \
   --http-method=GET \
   --uri=${CRON_URL}/cron/fetch-data \
   --oidc-service-account-email=rss-aggregator-scheduler@${PROJECT_ID}.iam.gserviceaccount.com   \
   --oidc-token-audience=${CRON_URL}/cron/fetch-data
gcloud beta scheduler jobs create http clean-job --schedule "every 8 hours" \
   --http-method=GET \
   --uri=${CRON_URL}/cron/cleanup \
   --oidc-service-account-email=rss-aggregator-scheduler@${PROJECT_ID}.iam.gserviceaccount.com   \
   --oidc-token-audience=${CRON_URL}/cron/cleanup
