from io import BytesIO
import os
import logging
from PyPDF2 import PdfFileReader

from s3_api import get_s3_client


logger = logging.getLogger()
logger.setLevel(logging.INFO)


s3_client = get_s3_client()


def read_file_RAW(bucket, key):
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        contents = response['Body'].read()
        return f"Length of read file contents: {len(contents)}"
    except Exception as e:
        return f"Failed to read contents of {bucket} / {key} due to: {e}"
    
    

def pdf_file_reader(bucket, key) -> str:
    try:
        response = s3_client.ObjectSummary(bucket, key).get()
        contents = response['Body'].read()
        pdf = PdfFileReader(BytesIO(contents))
        text = pdf.getFormTextFields()
        return text   
    except Exception as e:
        return f"Failed to read contents of {bucket} / {key} due to: {e}"
    
    
FILE_READERS = {
    "pdf": pdf_file_reader
}

def read_file(bucket, key):
    extension = key.split('.')[1]
    file_reader = FILE_READERS.get(extension)
    if file_reader:
        return file_reader(bucket, key)
    else:
        raise Exception(f"Files of type '{extension}' currently not supported")
        
