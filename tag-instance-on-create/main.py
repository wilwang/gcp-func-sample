import functions_framework
import os
from google.cloud import compute_v1

NETWORK_TAG = os.environ.get('NETWORK_TAG', 'networktag')

'''
NOTE: this function will add 1 network tag to any instances being created.
    You will likely want to create a logic filter to make sure you capture
    the specific instances that should have a network tag added.
'''
@functions_framework.cloud_event
def handle_gce_event(cloud_event):
    payload = cloud_event.data.get('protoPayload')
    resource_name = payload.get('resourceName')
    
    inst_arr = resource_name.split('/')
    project = inst_arr[inst_arr.index('projects')+1]
    zone = inst_arr[inst_arr.index('zones')+1]
    instance = inst_arr[inst_arr.index('instances')+1]

    # set_tags requires the tag fingerprint to avoid collisions from simultaneous API requests
    client = compute_v1.InstancesClient()
    inst = client.get(project=project, zone=zone, instance=instance)
    tag_fingerprint = inst.tags.fingerprint

    tags = compute_v1.Tags()
    tags.items = [NETWORK_TAG]
    tags.fingerprint = tag_fingerprint

    client.set_tags(project=project, zone=zone, instance=instance, tags_resource=tags)

    print(f'Set network tag {NETWORK_TAG} for {resource_name}')
