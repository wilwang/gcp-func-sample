# Google Cloud Function Samples

This repo is a collection of different types of Cloud Functions (v2) using both [Http triggers](https://cloud.google.com/functions/docs/calling/http) as well as [Eventarc triggers](https://cloud.google.com/functions/docs/calling/eventarc). Some of the functions work together as a simple ETL workflow, so there may be some common resources (service accounts, buckets, bq dataset, etc.) that may be re-used by different functions. 

Development was done using Cloud Shell, but if you are doing local development, I recommend looking at [Functions Framework](https://cloud.google.com/functions/docs/functions-framework). Some functions store files temporarily in `./tmp`. Cloud Functions have a `tmp` directory that is writable and is destroyed when the instance of the function is gone.

## Some common things to do

---

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

### Create Cloud Storage buckets

```
# bucket for where zip file will go
$ gcloud alpha storage buckets create gs://BUCKET_NAME

# bucket where the unzipped content will go
$ gcloud alpha storage buckets create gs://BUCKET_NAME_UNZIPPED
```

### (Optional) Create a service account and give it Bucket and Cloud Function roles

You can create a service account specifically for these functions or use default service accounts (e.g., Compute Engine). It is generally not recommended to use default service accounts since they usually have more privileges than you need. 

Give the service account roles required for these set of demo functions (Cloud Function, Cloud Run, Cloud Storage, and BigQuery Job User). Make sure to also give this service account bucket and object [permissions](https://cloud.google.com/storage/docs/access-control/iam-gsutil) on the specific buckets created earlier.

```
# Create service account
$ gcloud iam service-accounts create some-account-name --display-name="My Service Account" 

# Grant project level roles
$ gcloud projects add-iam-policy-binding PROJECT_ID --member='serviceAccount:some-account-name@project.iam.gserviceaccount.com' --role='roles/cloudfunctions.invoker' 
$ gcloud projects add-iam-policy-binding PROJECT_ID --member='serviceAccount:some-account-name@project.iam.gserviceaccount.com' --role='roles/run.invoker' 
$ gcloud projects add-iam-policy-binding PROJECT_ID --member='serviceAccount:some-account-name@project.iam.gserviceaccount.com' --role='roles/bigquery.jobUser'


# Grant roles specifically for the storage buckets
$ gsutil iam ch serviceAccount:some-account-name@project.iam.gserviceaccount.com:legacyBucketOwner gs://BUCKET_NAME
$ gsutil iam ch serviceAccount:some-account-name@project.iam.gserviceaccount.com:legacyObjectOwner gs://BUCKET_NAME
$ gsutil iam ch serviceAccount:some-account-name@project.iam.gserviceaccount.com:legacyBucketOwner gs://BUCKET_NAME_UNZIPPED
$ gsutil iam ch serviceAccount:some-account-name@project.iam.gserviceaccount.com:legacyObjectOwner gs://BUCKET_NAME_UNZIPPED
```

> Cloud Run invoker role is provisioned because Cloud Functions v2 is backed by Cloud Run.

### Grant the Cloud Storage service account Pub/Sub publisher role

Eventarc triggers leverage Pub/Sub, so the Pub/Sub publisher role must be provided to allow the Cloud Storage service to publish event messages to Pub/Sub. 

```
$ SERVICE_ACCOUNT="$(gsutil kms serviceaccount -p PROJECT_ID)"

$ gcloud projects add-iam-policy-binding PROJECT_ID --member="serviceAccount:${SERVICE_ACCOUNT}" --role='roles/pubsub.publisher'
```

### Create a BigQuery dataset

For details on how to create a BigQuery data set go to https://cloud.google.com/bigquery/docs/datasets. One important thing to keep in mind is the location of the dataset. Once the dataset is created, it cannot be changed.

```
bq --location=US mk -d \
    --default_table_expiration 3600 \
    --description "This is my dataset." \
    mydataset
```

### Grant the service account permissions for BigQuery

[Granting permission on a dataset](https://cloud.google.com/bigquery/docs/dataset-access-controls) might be easier to do in the console. Grant the service account Big Query Editor role on the dataset created above.

## Deploying Cloud Functions

Depending on whether you are deploying an HTTP trigger Cloud Function or Eventarch trigger Cloud Function, there will be different parameters to include. The commands below assume you are running from within the directory of your function code (Note: the `source` parameter is current directory). This is not a requirement. 

Check out https://cloud.google.com/functions/docs/deploy for more details around deploying Cloud Functions. 

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

> **NOTE**
>
> For the import-to-bq function, you may need to increase the [memory limit](https://cloud.google.com/functions/docs/configuring/memory) of the function when deploying
>
> Be aware that for [newer runtimes](https://cloud.google.com/functions/docs/configuring/env-var#newer_runtimes), GCP_PROJECT environment variable is not set

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
    --memory=512M
```

## Development Environment

Most of these functions were written in Python on Cloud Shell. I used virtualenv to isolate the environment for each function. 

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