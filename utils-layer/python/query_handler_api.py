from typing import Any, Dict

from bedrock_api import get_bedrock_client, get_langchain_client, get_embeddings_client, get_conversation_memory
from qa_api import qa_from_langchain_and_vectorstore, fetch_conv_qa
from qa_api import query_qa, query_conv, reset_conv
from vector_db_api import retrieve_pinecone_vectorstore


bedrock_client = get_bedrock_client()
langchain_client = get_langchain_client(bedrock_client)
embeddings_client = get_embeddings_client(bedrock_client)
vectorstore = retrieve_pinecone_vectorstore(bedrock_embeddings=embeddings_client)

qa = qa_from_langchain_and_vectorstore(langchain_client, vectorstore, with_sources=False)
qa_with_sources = qa_from_langchain_and_vectorstore(langchain_client, vectorstore)

qa_handlers = {
    ("conversation", True): lambda session_id, reset_conversation, query: query_conv(fetch_conv_qa(session_id, langchain_client, vectorstore, reset_conversation=reset_conversation), query),
    ("conversation", False): lambda session_id, reset_conversation, query: query_conv(fetch_conv_qa(session_id, langchain_client, vectorstore, reset_conversation=reset_conversation), query),
    ("single_shot", True): lambda session_id, reset_conversation, query: query_qa(qa_with_sources, query),
    ("single_shot", False): lambda session_id, reset_conversation, query: query_qa(qa, query)
}


def handle_query(input: Dict[str, Any]) -> Dict[str, Any]:
    mode = input["mode"]
    show_sources = input["show_sources"]
    
    session_id = input["session_id"]
    reset_conversation = input["reset_conversation"]
    query = input["query"]

    qa_handler = qa_handlers[(mode, show_sources)]
    result = qa_handler(session_id, reset_conversation, query)
    return result

    
