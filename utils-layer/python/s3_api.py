import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


s3_client = None

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
    
    s3_client.download_file(bucket, key, local_file_path)
