#!/bin/bash

# issue a few sample requests to the genAI-RAG prototype service

curl -H "Authorization: Bearer $COGNITO_ID_TOKEN" https://n2kqilxd7g.execute-api.us-east-1.amazonaws.com/api/qa

echo ""
echo ""

curl \
  -H "Authorization: Bearer $COGNITO_ID_TOKEN" \
  "https://n2kqilxd7g.execute-api.us-east-1.amazonaws.com/api/qa?mode=single_shot&show_sources=True&query=what+is+Agda"

echo ""
echo ""

curl -X POST -H "Authorization: Bearer $COGNITO_ID_TOKEN" \
    https://14cuqlv650.execute-api.us-east-1.amazonaws.com/Prod/qa/ \
   -H 'content-type: application/json' \
   -d '{"mode": "single_shot", "query": "what is Agda?", "show_sources": "True"}'
   
 