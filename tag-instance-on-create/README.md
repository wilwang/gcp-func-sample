# Trigger on Audit Log

This function will assign a network tag to a Compute Engine instance when it is created. There is not a direct event for Compute Engine, so we use [Audit Log triggers](https://cloud.google.com/functions/docs/tutorials/cloud-audit-logs) to execute the Cloud Function. 
<br />

> NOTE: [Audit Logs](https://cloud.google.com/logging/docs/audit) for Compute Engine must be turned on for this function to work. 
<br />

When [setting network tags](https://cloud.google.com/vpc/docs/add-remove-network-tags#gcloud) on a compute instance, you have to retrieve the tag fingerprints before you can set new tags. The purpose of the fingerprint is to avoid collisons from simultaneous API requests. For this function, I used the `google-cloud-compute` SDK to [retrieve an instance](https://cloud.google.com/python/docs/reference/compute/latest/google.cloud.compute_v1.services.instances.InstancesClient#google_cloud_compute_v1_services_instances_InstancesClient_get), and to [set the network tags](https://cloud.google.com/python/docs/reference/compute/latest/google.cloud.compute_v1.services.instances.InstancesClient#google_cloud_compute_v1_services_instances_InstancesClient_set_tags).

# Deploying the function

Make sure the service account has the correct permissions
- Compute Instance Admin (`roles/compute.instanceAdmin`)
- Cloud Function Invoker (`roles/cloudfunctions.invoker`)
- Cloud Run Invoker (`roles/run.invoker`)
- Eventarc Event Receiver (`roles/eventarc.eventReceiver`)

```
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:my-service-account@PROJECT_ID.iam.gserviceaccount.com" \
    --role='roles/eventarc.eventReceiver' \
    --role='roles/compute.instanceAdmin' \
    --role='roles/cloudfunctions.invoker' \
    --role='roles/run.invoker'
```

When deploying audit log triggered functions, you will need to supply the service name and service method into the event filters. Another thing of note is that the location of the trigger cannot be regional/multi-regional because we are dealing with Compute Engine which is zonal.

```
gcloud functions deploy tag-instance-on-create \
    --gen2 \
    --region=ZONE \
    --runtime=python39 \
    --source=. \
    --entry-point=handle_gce_event \
    --trigger-location="ZONE" \
    --trigger-service-account=my-service-account@PROJECT_ID.iam.gserviceaccount.com \
    --trigger-event-filters="type=google.cloud.audit.log.v1.written" \
    --trigger-event-filters="serviceName=compute.googleapis.com" \
    --trigger-event-filters="methodName=beta.compute.instances.insert" \
    --service-account=my-service-account@PROJECT_ID.iam.gserviceaccount.com
```