import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


s3_client = boto3.client('s3')

def read_file(bucket, key):
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        contents = response['Body'].read()
        return f"Length of read file contents: {len(contents)}"
    except Exception as e:
        return f"Failed to read contents of {bucket} / {key} due to: {e}"
    
    
def lambda_handler(event, context):
    log_info = ""
    log_info += "=== full event details: ===\n"
    log_info += f"{event}\n"
    logger.info(log_info)
    log_info = ""
    for r in event['Records']:
        bucketname = r['s3']['bucket']['name']
        newfilename = r['s3']['object']['key']
        log_info += f"Bucket / new file: {bucketname} / {newfilename}\n"
        log_info += f"{read_file(bucketname, newfilename)}\n"
    logger.info(log_info)
