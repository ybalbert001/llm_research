import boto3
import time
import os

def list_s3_objects(s3_client,bucket_name, prefix=''):
    objects = []
    paginator = s3_client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    # iterate over pages
    for page in page_iterator:
        # loop through objects in page
        if 'Contents' in page:
            for obj in page['Contents']:
                yield obj
        # if there are more pages to fetch, continue
        if 'NextContinuationToken' in page:
            page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix,
                                                ContinuationToken=page['NextContinuationToken'])

def copy_files_between_buckets(source_bucket, destination_bucket):
    # Create a new S3 client
    access_key='AKIARRYBF7F2BS5L6D5Q'
    secret_key='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'
    s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

    # List objects in the source bucket
    idx = 0
    for item in list_s3_objects(s3, source_bucket, prefix='oa_comm/txt/all/'):
        try:
            source_key = item['Key']
            destination_filename = os.path.basename(source_key)
            destination_key = 'ai-content/{}/{}'.format('batch', destination_filename)
            copy_source = {'Bucket': source_bucket, 'Key': source_key}
            print("copy from {} to {}".format(source_key, destination_key))
            s3.copy_object(CopySource=copy_source, Bucket=destination_bucket, Key=destination_key)
            if idx < 10000:
                idx += 1
            else:
                break
        except Exception as e:
            print(f"failed with: {str(e)}")

# Example usage
source_bucket = 'pmc-oa-opendata'
destination_bucket = '106839800180-23-06-25-10-55-20-bucket'

copy_files_between_buckets(source_bucket, destination_bucket)