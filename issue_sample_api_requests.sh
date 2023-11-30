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
