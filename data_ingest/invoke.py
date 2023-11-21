import os
import logging

from doc_handler_api import handle_document


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    log_info = "=== full bucket event details: ===\n"
    log_info += f"{event}\n"
    logger.info(log_info)
    log_info = ""
    for r in event['Records']:
        bucket = r['s3']['bucket']['name']
        key = r['s3']['object']['key']
        log_info += f"Bucket / new object: {bucket} / {key}\n"
        logger.info(log_info)
    
        handle_document(bucket, key)
