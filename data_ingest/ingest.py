import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("=== full event details: ===")
    logger.info(event)
    logger.info("=== focussed event details: ===")
    logger.info(event.Records[0].s3)
