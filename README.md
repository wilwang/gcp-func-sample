# Google Cloud Function Samples

<p>
This repo is a collection of different types of Cloud Functions (v2) using both [Http triggers](https://cloud.google.com/functions/docs/calling/http) as well as [Eventarc triggers](https://cloud.google.com/functions/docs/calling/eventarc). Some of the functions work together as a simple ETL workflow, so there may be some common resources (service accounts, buckets, etc.) that may be re-used by different functions. 
</p>

<p>
Development was done using Cloud Shell, but if you are doing local development, I recommend looking at [Functions Framework](https://cloud.google.com/functions/docs/functions-framework). Some functions store files temporarily in `./tmp`. Cloud Functions have a `tmp` directory that is writable and is destroyed when the instance of the function is gone.
</p>

## Some common things to do

### Enable some APIs

```
$ gcloud services enable \
    artifactregistry.googleapis.com \
    cloudfunctions.googleapis.com \
    cloudbuild.googleapis.com \
    eventarc.googleapis.com \
    run.googleapis.com \
    logging.googleapis.com \
    pubsub.googleapis.com
```

### Create a Cloud Storage bucket

```
$ gcloud alpha storage buckets create gs://BUCKET_NAME
```

### (Optional) Create a service account and give it Bucket and Cloud Function roles

You can create a service account specifically for these functions or use default service accounts (e.g., Compute Engine). It is generally not recommended to use default service accounts since they usually have more privileges than you need.

```
$ gcloud iam service-accounts create some-account-name --display-name="My Service Account" 

$ gcloud projects PROJECT_ID \ 
    --member='serviceAccount:some-account-name@project.iam.gserviceaccount.com' \
    --role='roles/cloudfunctions.invoker' \
    --role='roles/run.invoker' \
    --role='roles/storage.legacyBucketOwner' \
    --role='roles/storage.legacyObjectOwner'
```

> Cloud Run invoker role is provisioned because Cloud Functions v2 is backed by Cloud Run.

### Grant the Cloud Storage service account Pub/Sub publisher role

Eventarc triggers leverage Pub/Sub, so the Pub/Sub publisher role must be provided to allow the Cloud Storage service to publish event messages to Pub/Sub. 

```
$ SERVICE_ACCOUNT="$(gsutil kms serviceaccount -p PROJECT_ID)"

$ gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role='roles/pubsub.publisher'
```

## Deploying Cloud Functions

<p>
Depending on whether you are deploying an HTTP trigger Cloud Function or Eventarch trigger Cloud Function, there will be different parameters to include. The commands below assume you are running from within the directory of your function code (Note: the `source` parameter is current directory). This is not a requirement. 
</p>

<p>
Check out https://cloud.google.com/functions/docs/deploy for more details around deploying Cloud Functions. 
</p>

### HTTP Trigger

```
$ gcloud functions deploy FUNCTION_NAME \
    --gen2 \
    --runtime=python30 \
    --entry-point=http_handler \
    --source=. \
    --region=REGION \
    --project=PROJECT_NAME \
    --trigger-http \
    --env-vars-file=env.yaml
    --run-service-account=SERVICE ACCOUNT
```

### Eventarc Trigger

The command below deploys a function that gets triggered whenever an object is added to a Cloud Storage bucket. To see all the different Eventarc triggers that are supported, go to https://cloud.google.com/eventarc/docs/reference/supported-events.

```
$ gcloud functions deploy FUNCTION_NAME \
    --gen2 \
    --runtime=python39 \
    --entry-point=ENTRY_POINT \
    --source=. \
    --region=REGION \
    --project=PROJECT_ID \
    --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
    --trigger-event-filters="bucket=BUCKET NAME" \
    --trigger-location="BUCKET LOCATION"
    --env-vars-file=env.yaml
```

## Development Environment

<p>
Most of these functions were written in Python on Cloud Shell. I used virtualenv to isolate the environment for each function. 
</p>

To create virtualenv

```
$ virtualenv -p python3 .venv
```

To activate

```
$ source .venv/bin/activate
```

To deactivate

```
$ deactivate
```

Install dependencies

```
$ pip install -r requirements.txt
```