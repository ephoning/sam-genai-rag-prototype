import json
import logging
import os

from vector_db_api import create_pinecone_index


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    
    index_name = os.environ['PINECONE_INDEX_NAME']
    api_key = os.environ["PINECONE_API_KEY"]
    environment = os.environ["PINECONE_ENVIRONMENT"]
    dimension = int(os.environ["EMBEDDING_DIMENSION"])
    
    logger.info(f"Initialize Pincone index with {index_name}/{api_key}/{environment}/{dimension}")
    create_pinecone_index(index_name, api_key, environment, dimension, metric='dotproduct', verbose=True)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Initialized Pincone index with {index_name}/{api_key}/{environment}/{dimension}",
            # "location": ip.text.replace("\n", "")
        }),
    }
