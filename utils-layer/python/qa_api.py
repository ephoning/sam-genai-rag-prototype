import os
from typing import Any

from langchain.chains import ConversationalRetrievalChain
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.memory import ConversationBufferMemory
from langchain.chains import RetrievalQA
from langchain.chains import RetrievalQAWithSourcesChain

from constants import *

default_max_token_limit = os.environ["DEFAULT_MAX_TOKEN_LIMIT"]


def qa_from_langchain_and_vectorstore_v1(langchain_client, vectorstore, with_sources=True) -> Any:
    """
    integrate / tie together the vector store and actual LLM model's text (answer) generation
    
    note: uses RetrievalQAWithSourcesChain to get source documents 
          (result/output contains 'question', 'answer', etc.)
    """
    if with_sources:
        qa = RetrievalQAWithSourcesChain.from_chain_type(
            llm=langchain_client, 
            chain_type="stuff", 
            retriever=vectorstore.as_retriever(), 
            return_source_documents=True)
    else:
        qa = RetrievalQA.from_chain_type(
            llm=langchain_client, 
            chain_type="stuff", 
            retriever=vectorstore.as_retriever())
    return qa


def qa_from_langchain_and_vectorstore_v2(langchain_client, vectorstore, with_sources=True) -> Any:
    """
    integrate / tie together the vector store and actual LLM model's text (answer) generation
    
    note: uses RetrievalQA to get source documents 
          (result/output contains 'query', 'result', etc. (differs from above...))
    """
    if with_sources:
        qa = RetrievalQA.from_chain_type(
            llm=langchain_client, 
            chain_type="stuff", 
            retriever=vectorstore.as_retriever(), 
            return_source_documents=True,
            chain_type_kwargs={"prompt": ANTHROPIC_QA_PROMPT_TEMPLATE})
    else:
        qa = RetrievalQA.from_chain_type(
            llm=langchain_client, 
            chain_type="stuff", 
            retriever=vectorstore.as_retriever())
    return qa


def conv_qa_from_langchain_and_vectorstore_v2(langchain_client, vectorstore, conversation_memory, 
                                              chain_type='stuff', max_token_limit=default_max_token_limit, verbose=False) -> Any:
    """
    contstruct conversational Q&A instance
    """
    memory_chain = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conv_qa = ConversationalRetrievalChain.from_llm(
        llm=langchain_client, 
        retriever=vectorstore.as_retriever(), 
        memory=conversation_memory,                                            
        condense_question_prompt=CONDENSE_QUESTION_PROMPT,
        verbose=verbose, 
        chain_type=chain_type,
        max_tokens_limit=max_token_limit
    )
    return conv_qa
    

def qa_from_langchain_and_vectorstore(langchain_client, vectorstore, with_sources=True) -> Any:
    """
    use v1 for now...
    """
    return qa_from_langchain_and_vectorstore_v1(langchain_client, vectorstore, with_sources)


def query_qa(qa, query) -> Any:
    if type(qa) == RetrievalQAWithSourcesChain:
        result = qa(query)
    else:
        result = qa.run(query)
    return result


def query_conv(conv_qa, query) -> Any:
    result = conv_qa.run({'question': query })
    return result


def reset_conv(conv_memory):
    conv_memory.clear()