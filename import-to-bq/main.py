import functions_framework
import os
import io
import re
import pandas as pd
import datetime
from google.cloud import storage
from google.cloud import bigquery

PROJECT_ID = os.environ.get('GCP_PROJECT', '')
GCS_BUCKET = os.environ.get('GCS_BUCKET_NAME', '')
BQ_DATASET = os.environ.get('BQ_DATASET_ID', '')
BQ_TABLE = os.environ.get('BQ_TABLE_NAME', '')

def read_from_gcs(bucket, file):
    client = storage.Client(
        project=PROJECT_ID
    )
    bucket = client.get_bucket(bucket)
    blob = bucket.blob(file)
    data = blob.download_as_text()

    return data

def clean_data(datastr):
    # stupid \r\n line terminator poses a problem for dataframe.read_csv which only allows 1 char
    data = datastr.replace('\r\n', '\n') 
    strio = io.StringIO(data)
    df = pd.read_csv(
        strio, 
        dtype=str, # keep the leading 0,
        sep=',', 
        header=0, 
        lineterminator='\n')

    # fix column names
    df.columns = df.columns.str.replace(' ', '_')
    df.columns = df.columns.str.lower()

    # remove special chars from numbers
    df['eligibles'] = df['eligibles'].str.replace(',', '')
    df['enrolled'] = df['enrolled'].str.replace(',', '')
    df['penetration'] = df['penetration'].str.replace('%', '')
    
    # convert into int type
    df['eligibles'] = pd.to_numeric(df['eligibles'], errors='coerce').astype('Int64')
    df['enrolled'] = pd.to_numeric(df['enrolled'], errors='coerce').astype('Int64')
    df['penetration'] = pd.to_numeric(df['penetration'], errors='coerce').astype('float')

    # have to scrub bad data from data source
    return df[df['state_name'].str.contains('Pending State Designation')==False]

def import_df(df, table_id):
    client = bigquery.Client(
        project=PROJECT_ID
    )
    job_config = bigquery.LoadJobConfig(
        # overrides BQ default schema detection for these columns
        schema=[
            bigquery.SchemaField("fipsst", "STRING"),
            bigquery.SchemaField("fipscnty", "STRING"),
            bigquery.SchemaField("fips", "STRING"),
            bigquery.SchemaField("ssast", "STRING"),
            bigquery.SchemaField("ssacnty", "STRING"),
            bigquery.SchemaField("ssa", "STRING")
        ],
        write_disposition="WRITE_TRUNCATE"
    )
    job = client.load_table_from_dataframe(
        df, 
        table_id, 
        job_config=job_config
    )
    job.result()
    table = client.get_table(table_id)
    print(f'Loaded {table.num_rows} into {table_id}')

def import_csv_to_bq(gsurl, table_id):
    client = bigquery.Client(
        project=PROJECT_ID
    )
    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        source_format=bigquery.SourceFormat.CSV
    )
    load_job = client.load_table_from_uri(
        gsurl, table_id, job_config=job_config
    )
    load_job.result()
    dest_table = client.get_table(table_id)
    print(f'Loaded {dest_table.num_rows} rows from {gsurl}')

@functions_framework.cloud_event
def handle_gcs_event(cloud_event):
    data = cloud_event.data
    bucket = data['bucket']
    file = data['name']

    print(PROJECT_ID)
    print(GCS_BUCKET)
    print(BQ_DATASET)
    print(BQ_TABLE)

    print(bucket)
    print(file)

    try:
        #include '.csv' JUST IN CASE we encounter another \d{4}_\d{2} in the file name
        dt_str = re.findall(r'\d{4}_\d{2}.csv', file)[0].replace('.csv', '')
        file_dt = datetime.datetime.strptime(dt_str, '%Y_%m')
        # add '01' at the end to enable bq to index tables by date; needs YYYYMMDD format
        fmt_dt = file_dt.strftime('%Y%m01')
        table_id = f'{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}_{fmt_dt}'

        print(table_id)

        data = read_from_gcs(bucket, file)
        df = clean_data(data)
        import_df(df, table_id)
    except Exception as e:
        print(e)
    