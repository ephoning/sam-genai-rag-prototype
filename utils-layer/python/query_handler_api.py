from typing import Any, Dict

from bedrock_api import get_bedrock_client, get_langchain_client, get_embeddings_client, get_conversation_memory
from qa_api import qa_from_langchain_and_vectorstore, conv_qa_from_langchain_and_vectorstore_v2
from qa_api import query_qa, query_conv, reset_conv
from vector_db_api import retrieve_pinecone_vectorstore


bedrock_client = get_bedrock_client()
langchain_client = get_langchain_client(bedrock_client)
embeddings_client = get_embeddings_client(bedrock_client)
conversation_memory = get_conversation_memory()
vectorstore = retrieve_pinecone_vectorstore(bedrock_embeddings=embeddings_client)

qa = qa_from_langchain_and_vectorstore(langchain_client, vectorstore, with_sources=False)
qa_with_sources = qa_from_langchain_and_vectorstore(langchain_client, vectorstore)
conv_qa = conv_qa_from_langchain_and_vectorstore_v2(langchain_client, vectorstore, conversation_memory) 

qa_handlers = {
    ("conversation", True): lambda q: query_conv(conv_qa, q),
    ("conversation", False): lambda q: query_conv(conv_qa, q),
    ("single_shot", True): lambda q: query_qa(qa_with_sources, q),
    ("single_shot", False): lambda q: query_qa(qa, q)
}


def handle_query(input: Dict[str, Any]) -> Dict[str, Any]:
    session_id = input["session_id"]
    query = input["query"]
    mode = input["mode"]
    reset_conversation = input["reset_conversation"]
    show_sources = input["show_sources"]

    if reset_conversation:    
        reset_conv(conversation_memory)
    
    qa_handler = qa_handlers[(mode, show_sources)]
    result = qa_handler(query)
    return result

    
