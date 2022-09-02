# Enable necessary APIs

```
gcloud services enable \
  artifactregistry.googleapis.com \
  cloudfunctions.googleapis.com \
  cloudbuild.googleapis.com \
  eventarc.googleapis.com \
  run.googleapis.com \
  logging.googleapis.com \
  pubsub.googleapis.com
```

# Create a destination bucket

```
$ gcloud alpha storage buckets create gs://BUCKET_NAME
```

# Use python virtualenv

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

# Deploy function with configuration

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
```

# Test the function

```
$ curl  -H "Authorization: bearer $(gcloud auth print-identity-token)" FUNCTION_URL
```

