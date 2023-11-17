import boto3


def get_s3_client():
    s3_client = boto3.resource("s3")
    return s3_client
