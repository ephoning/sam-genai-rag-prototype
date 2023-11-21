import json
import logging
import os

from vector_db_api import create_pinecone_index


logger = logging.getLogger()
logger.setLevel(logging.INFO)


index_name = os.environ['DEFAULT_PINECONE_INDEX_NAME']
api_key = os.environ["DEFAULT_PINECONE_API_KEY"]
environment = os.environ["DEFAULT_PINECONE_ENVIRONMENT"]
dimension = int(os.environ["EMBEDDING_DIMENSION"])
metric = os.environ["DEFAULT_PINECONE_METRIC"]


def lambda_handler(event, context):
    logger.info(f"Initialize Pincone index with {index_name}/{api_key}/{environment}/{dimension}")
    create_pinecone_index(index_name, api_key, environment, dimension, metric=metric, verbose=True)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Initialized Pincone index with {index_name}/{api_key}/{environment}/{dimension}/{metric}",
            # "location": ip.text.replace("\n", "")
        }),
    }
