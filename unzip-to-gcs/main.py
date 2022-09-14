import os
import functions_framework
import zipfile
import glob
import io
from google.cloud import storage

# Cloud function have access to ./tmp/ for temporary storage
WORK_DIR = './tmp/'
PROJECT_ID = os.environ.get('GCP_PROJECT', '')
GCS_BUCKET = os.environ.get('GCS_BUCKET_NAME', '')

def download_from_gcs(bucket, file):
    fpath = f'{WORK_DIR}{file}'

    client = storage.Client(
        project=PROJECT_ID
    )
    bucket = client.get_bucket(bucket)
    blob = bucket.blob(file)
    blob.download_to_filename(fpath)

    return fpath

def get_filepaths_by_ext(dir, ext):
    search_dir = f'{dir}/**/*{ext}'
    files = glob.glob(search_dir, recursive=True)

    return files

def upload_to_gcs(filepath):
    client = storage.Client(
        project=PROJECT_ID
    )
    filename = os.path.basename(filepath)
    bucket = client.bucket(GCS_BUCKET)
    blob = storage.Blob(filename, bucket, chunk_size=262144)
    blob.upload_from_filename(filepath)
    
@functions_framework.cloud_event
def handle_gcs_event(cloud_event):
    data = cloud_event.data
    bucket = data['bucket']
    file = data['name']

    fpath = download_from_gcs(bucket, file)
    try:
        with zipfile.ZipFile(fpath, 'r') as zip_ref:
            zip_ref.extractall(WORK_DIR)

        fpaths = get_filepaths_by_ext(WORK_DIR, '.csv')

        for fpath in fpaths:
            upload_to_gcs(fpath)

    except Exception as e:
        print(e)
