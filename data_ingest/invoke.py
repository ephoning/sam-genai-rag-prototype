import os
import logging

from doc_handler_api import *


logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
        log_info += f"{read_file(bucketname, newfilename)[:32]}\n"
    logger.info(log_info)
