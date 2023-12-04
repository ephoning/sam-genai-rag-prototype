#!/bin/bash

# issue a few sample requests to the genAI-RAG prototype service

# inspect 'Invoke URL' values in API Gateway to find the value for HOST_ID
HOST_ID=14cuqlv650

curl \
   -H "Authorization: Bearer $COGNITO_ID_TOKEN" \
   "https://$HOST_ID.execute-api.us-east-1.amazonaws.com/api/qa"

echo ""
echo ""

curl \
   -H "Authorization: Bearer $COGNITO_ID_TOKEN" \
   "https://$HOST_ID.execute-api.us-east-1.amazonaws.com/api/qa?mode=single_shot&show_sources=True&query=what+is+Agda"

echo ""
echo ""

curl -X POST \
   -H "Authorization: Bearer $COGNITO_ID_TOKEN" \
   "https://$HOST_ID.execute-api.us-east-1.amazonaws.com/Prod/qa/" \
   -H 'content-type: application/json' \
   -d '{"mode": "single_shot", "query": "what is Agda?", "show_sources": "True"}'
   
 