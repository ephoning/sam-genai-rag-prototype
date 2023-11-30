#!/bin/bash

# Authenticate to Cognito, resulting in setting of the COGNITO_ID_TOKEN env var for subsequent use in API requests Authorization header
# parameters: Cognito user name (user's enail address) + Cognito password
if [ $# -ne 2 ]; then
   echo "Usage: $ . get_cognito_id_token <cognito user name / email> <cognito password>"
   echo "       Notice the '.' at the start of the command - this makes sure that the 'COGNITO_ID_TOKEN' env var is set in the calling shell"
   echo "(it is expected that the COGNITO_CLIENT_ID env var has been set based on the outputs from 'sam deploy' invocation)"
   exit -1
fi

COGNITO_USER_EMAIL=$1
COGNITO_PASSWORD=$2

echo "Getting ACCESS and ID tokens for client-id = $COGNITO_CLIENT_ID, user name= $COGNITO_USER_EMAIL, and password = ***"

aws cognito-idp initiate-auth \
   --auth-flow USER_PASSWORD_AUTH \
   --auth-parameters "USERNAME=$COGNITO_USER_EMAIL,PASSWORD=$COGNITO_PASSWORD" \
   --client-id $COGNITO_CLIENT_ID \
   --output json \
   --region us-east-1 \
   > cognito_response.json
 
cat cognito_response.json

# note: using '-r' to avoid including the surrounding double quotes in the captured token values 
#export COGNITO_ACCESS_TOKEN=`jq -r '..|.AccessToken?|select(.)' cognito_response.json`
export COGNITO_ID_TOKEN=`jq -r '..|.IdToken?|select(.)' cognito_response.json`

echo "exported COGNITO_ACCESS_TOKEN and COGNITO_ID_TOKEN"

rm cognito_response.json
 
