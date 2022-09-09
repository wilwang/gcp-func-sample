import datetime
import calendar
import requests
import os
import io
from google.cloud import storage

# Cloud function have access to ./tmp/ for temporary storage
WORK_DIR = './tmp/'
DL_URL_ROOT = os.environ.get('DL_URL_ROOT', 'https://www.cms.gov/files/zip/ma-statecounty-penetration-')
PROJECT_ID = os.environ.get('GCP_PROJECT', '')
GCS_BUCKET = os.environ.get('GCS_BUCKET_NAME', '')

def build_url(mo, yr):
    url = DL_URL_ROOT + mo + '-' + yr + '.zip'
    return str.lower(url)

def upload_to_gcs(filepath):
    client = storage.Client(
        project=PROJECT_ID
    )
    filename = os.path.basename(filepath)
    bucket = client.bucket(GCS_BUCKET)
    blob = storage.Blob(filename, bucket, chunk_size=262144)

    with open(filepath, 'rb') as fh:
        buf = io.BytesIO(fh.read())
        blob.upload_from_file(buf, content_type='application/zip')

def http_handler(request):
    targ_date = datetime.date.today()

    # expect query param date=<YYYYMM>
    args = request.args
    arg_date = args.get("date")

    if arg_date is not None:
        try:
            targ_date = datetime.datetime.strptime(arg_date, '%Y%m')
        except Exception as e:
            msg = f'Error parsing {arg_date} to date\n{e}'
            print(msg)
            return msg, 400

    mo_num = targ_date.strftime('%m')
    mo_name = targ_date.strftime('%B')
    yr = targ_date.strftime('%Y')

    fname = yr + mo_num + '.zip'
    fpath = WORK_DIR + fname
    dl_url = build_url(mo_name, yr)
    print(f'Downloading from {dl_url}')

    try: 
        r = requests.get(dl_url)

        if r.status_code != 200:
            msg = f'{r.status_code}: Error retrieving {dl_url}'
            print(msg)
            return msg, r.status_code

        open(fpath, 'wb').write(r.content)
        upload_to_gcs(fpath)
        print(f'Finished downloading {fname} from {dl_url}')
        return fname, 200
    except Exception as e:
        msg = f'Error downloading and uploading to bucket\n{e}'
        print(msg)
        return msg, 500
