from io import BytesIO
import os
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging
import traceback
from typing import Any, Dict, List

from s3_api import download_object
from bedrock_api import get_bedrock_client, get_embeddings_client
from vector_db_api import populate_pinecone_index


local_temp_storage_root = '/tmp'


bedrock_client = None
embeddings_client = None

document_loader_constructors = {
    "pdf": lambda file_path: PyPDFLoader(file_path)
}

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_clients():
    global bedrock_client
    global embeddings_client
    embeddings_model_id = os.environ['DEFAULT_EMBEDDINGS_MODEL_ID']
    
    logger.info(f"getting bedrock (embeddings) client for model with id '{embeddings_model_id}'")
    if not bedrock_client:
        bedrock_client = get_bedrock_client()
    if not embeddings_client:
        embeddings_client = get_embeddings_client(bedrock_client, embeddings_model_id)
    return bedrock_client, embeddings_client

    
def create_doc_chunks(local_file_path: str, metadata: Dict[str, Any], chunk_size=1000, chunk_overlap=100) -> List[Any]:
    extension = local_file_path.split('.')[1]
    doc_loader = document_loader_constructors.get(extension)(local_file_path)
    if doc_loader:
        document = doc_loader.load()
        for document_fragment in document:
            document_fragment.metadata = metadata
        logger.info(f'doc length: {len(document)}\n')
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        doc_chunks = text_splitter.split_documents(document)
        logger.info(f'After the split we have {len(doc_chunks)} documents.')
        return doc_chunks


def handle_document(bucket, key):
    _, embeddings_client = get_clients()

    index_name = os.environ['PINECONE_INDEX_NAME']
    local_file_path = f"{local_temp_storage_root}/{key}"
    metadata = dict(name=key)
    
    try:
        download_object(bucket, key, local_file_path)
        doc_chunks = create_doc_chunks(local_file_path, metadata)
        logger.info(f"first doc chunk details: {doc_chunks[0]}")
        populate_pinecone_index(doc_chunks, embeddings_client, index_name, verbose=True)
        
    except Exception as e:
        logger.error(f"Failed to process contents of '{bucket}' / '{key}' due to: '{e}' - ignoring")
        tb = traceback.format_exc()
        logger.error(f"Traceback: {tb}")
        
    finally:
        if os.path.exists(local_file_path):
            os.remove(local_file_path)
            
        