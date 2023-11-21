import boto3
import logging
import os
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)


s3_client = None

# sometimes bigger files are detected to have arrived but are not readably yet, so support retrying
max_retries = 3
retry_delay = 20  # seconds

def get_s3_client():
#    s3_client = boto3.resource("s3")
    return boto3.client("s3")


def get_object_body(bucket, key):
    global s3_client
    if not s3_client:
        s3_client = get_s3_client()
        
    response = s3_client.get_object(Bucket=bucket, Key=key)
    body = response['Body'].read()
    return body


def download_object(bucket, key, local_file_path):
    global s3_client
    if not s3_client:
        s3_client = get_s3_client()
    
    retry = 1
    while retry <= max_retries:
        try:
            s3_client.download_file(bucket, key, local_file_path)
            return
        except:
            logger.info(f"Download file '{key}' from S3 bucket '{bucket}' failed; sleep then retry...")
            time.sleep(retry_delay)
            retry += 1
            
    logger.error(f"Download of files '{key}' from S3 bucket '{bucket}' failed even after {max_retries} tries; ignoring")