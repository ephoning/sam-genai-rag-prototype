import os

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY") or "4995b4bc-bb2d-4dfe-8bb3-992a10ea9854"
PINECONE_ENVIRONMENT = os.environ.get("PINECONE_ENVIRONMENT") or "gcp-starter"

AGDA_PINECONE_INDEX_NAME = 'agda-knowledge-base'
