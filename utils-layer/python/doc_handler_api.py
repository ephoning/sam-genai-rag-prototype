from io import BytesIO
import os
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging
from typing import Any, Dict, List

from s3_api import download_object


local_temp_storage_root = '/tmp'


logger = logging.getLogger()
logger.setLevel(logging.INFO)


# def txt_file_reader(bucket, key) -> str:
#     contents = get_object_body(bucket, key)
#     return contents

    
# def pdf_file_reader(bucket, key) -> str:
#     contents = get_object_body(bucket, key)
#     reader = PdfReader(BytesIO(contents))
#     text = ''
#     for page in reader.pages:
#       text += page.extract_text() 
#     return text   

    
# file_readers = {
#     "pdf": pdf_file_reader,
#     "txt": txt_file_reader
# }


# def read_file(bucket, key):
#     extension = key.split('.')[1]
#     file_reader = file_readers.get(extension)
#     if file_reader:
#         return file_reader(bucket, key)
#     else:
#         raise Exception(f"Files of type '{extension}' currently not supported")
        

document_loader_constructors = {
    "pdf": lambda file_path: PyPDFLoader(file_path)
}


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
    local_file_path = f"{local_temp_storage_root}/{key}"
    metadata = dict(name=key)
    
    try:
        download_object(bucket, key, local_file_path)
        doc_chunks = create_doc_chunks(local_file_path, metadata)
        logger.info(f"first doc chunk details: {doc_chunks[0]}")
        
    except Exception as e:
        logger.error(f"Failed to read contents of '{bucket}' / '{key}' due to: '{e}' - ignoring")
        
    finally:
        if os.path.exists(local_file_path):
            os.remove(local_file_path)
            
        