from langchain.vectorstores import Pinecone
import logging
import pinecone
import time
from typing import Any


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_pinecone_index(index_name: str, api_key: str, environment: str, dimension: int, metric='dotproduct', verbose=False) -> None:
    pinecone.init(api_key=api_key, environment=environment)
    logger.info("Pinecone initialized")
    if index_name in pinecone.list_indexes():
        logger.info(f"Deleting pre-existing index named '{index_name}'")
        pinecone.delete_index(index_name)
        logger.info(f"Creating index named '{index_name}' with dimension '{dimension}' and metric '{metric}'")
    pinecone.create_index(name=index_name, dimension=dimension, metric=metric)
    # wait for index to finish initialization
    while not pinecone.describe_index(index_name).status["ready"]:
        time.sleep(1)
    if verbose:
        logger.info(f"Created index named '{index_name}' with dimension '{dimension}' and metric '{metric}'")
        index = pinecone.Index(index_name)
        index.describe_index_stats()


def populate_pinecone_index(docs, bedrock_embeddings, index_name, verbose=False):
    """
    populate Pincone index with the document embeddings
    """
    logger.info(f"add docs and their embeddings to pincone index using '{bedrock_embeddings}'/'{index_name}'")
    docsearch = Pinecone.from_documents(documents=docs, embedding=bedrock_embeddings, index_name=index_name)
    if verbose:
        index = pinecone.Index(index_name)
        index.describe_index_stats()




def retrieve_pinecone_vectorstore(bedrock_embeddings, index_name, api_key, environment, text_field='text') -> Any:
    """
    register/connect Pinecone index to langchain
    """
    pinecone.init(api_key=api_key, environment=environment)
    index = pinecone.Index(index_name)
    vectorstore = Pinecone(index, bedrock_embeddings, text_field)
    return vectorstore


def query_vectorstore(vectorstore, query, k=3) -> Any:
    result = vectorstore.similarity_search(query, k=3) 
    return result
