import json
import logging
import os

from vector_db_api import pinecone_index_exists, destroy_pinecone_index, create_pinecone_index


logger = logging.getLogger()
logger.setLevel(logging.INFO)


default_index_name = os.environ["DEFAULT_PINECONE_INDEX_NAME"]
default_api_key = os.environ["DEFAULT_PINECONE_API_KEY"]
default_environment = os.environ["DEFAULT_PINECONE_ENVIRONMENT"]
default_dimension = int(os.environ["DEFAULT_EMBEDDING_DIMENSION"])
default_metric = os.environ["DEFAULT_PINECONE_METRIC"]

first_document_sets_embedding_dimension = os.environ["FIRST_DOCUMENT_SETS_EMBEDDING_DIMENSION"] == 'True' or os.environ["FIRST_DOCUMENT_SETS_EMBEDDING_DIMENSION"]
dimension = int(os.environ["DEFAULT_EMBEDDING_DIMENSION"])

metric = os.environ["DEFAULT_PINECONE_METRIC"]


def lambda_handler(event, context):
    index_exists = pinecone_index_exists(default_index_name, default_api_key, default_environment) 
    if first_document_sets_embedding_dimension:
        if index_exists:
            destroy_pinecone_index(default_index_name, default_api_key, default_environment)
            message = f"Destroyed Pinecone index named {default_index_name} with api_key={default_api_key} / environment={default_environment} - will be re-created 'JIT' on document arrival in landing zone S3 bucket"
        else:
            message = f"No-op; Pinecone index named {default_index_name} with api_key={default_api_key} / environment={default_environment} does not exist - will be created 'JIT' on document arrival in landing zone S3 bucket"
    else:
        if index_exists:
            destroy_pinecone_index(default_index_name, default_api_key, default_environment)
        create_pinecone_index(default_index_name, default_api_key, default_environment, default_dimension, default_metric, verbose=True)
        message = f"(Re-)created Pinecone index named {default_index_name} with api_key={default_api_key} / environment={default_environment} / dimension={default_dimension} / metric={default_metric}"

    logger.info(message)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": message
        }),
    }
