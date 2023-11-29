# sam-genai-rag-prototype

This project is an example of an AWS SAM orchestrated set of resources that form an genAI RAG application.
It is intended to serve as a baseline for the development of a PoC for Medtronics.
The diagram below outlines the overall structure of the application:

![](aws-bedrock-arch-3-edited.jpg)


NOTE: access to desired LLM & embeddings models needs to be requested at the following location:
![](https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess)

Currently, it is unclear how to use AWS SAM to provision a service from the AWS Marketplace and capture access credentials for such a service for use in the project's AWS SAM template.
The credentials for the Pincone vector DB that was provisioned for the AWS Bedrock workshop have for now been hardcoded in the appropriate 'Globals' in template.yaml.

Initialization of the index for the vector DB and fetching a connection is done in the 'static initialization' section of the DataIngest lambda - i.e., outside of the handler function. function.


## AWS Lambda Layers

### boto3-layer

This to get a new enough boto3 version that provides access to the 'bedrock' service

populate using:
```bash
$ cd boto3-layer/python
$ pip install boto3==1.29.2 -t .
```

### libs-layer

This to provide multiple shared dependencies

populate using:
```bash
$ cd libs-layer/python
$ pip install "urllib3<2" -t .
$ pip install langchain -t .
$ pip install PyPDF2 -t .      # maybe remove?!?
$ pip install pinecone-client -t . 
$ pip install pypdf -t .
$ pip install anthropic -t .
```

### utils-layer

This to provide local custom utility functionality across lambda functions

location:
```bash
utils-layer/python
```

-------------------
## Development / deployment cycle
After having modified code or configuration artifacts, the following steps are to be executed to re-build and re-deploy the 'stack':
```bash
$ cd <project base directory>
$ sam build && sam deploy
```

-------------------
## Manual resource creation and/or configuration
Currently, not all required resources are created or configured are represented in 'template.yaml':
- IAM policies to allow the required lambdas to access Bedrock model instances
- API Gateway deployment of the desired 'stages' (this IS done by AWS SAM tooling if NO 'Auth' property is defined for a Function entry, but for now needs to be done using e.g., the AWS web UI if the 'Auth' property is present)

Currently, IAM related configuration and/or resource creation is accomplished using the AWS' web UI.

* Allow the 'data ingest' lambda to invoke models per:
```
      using the IAM UI
      - in sam-genai-rag-prototype CloudFormation stack, browse to ...dataiingestfunctionrole...
      - select: Add permissions - Create inline policy

      - select: Select a service: bedrock
      - Actions allowed
        - Effect radiobutton: 'Allow'
        - select 'Read' - 'all read actions'
          note that'Read' includes 'InvokeModel'
                
      - Resources
        - select 'All' radiobutton for now

      - click 'Next'
      - Review and create
        - give policy name; e.g., 'dataingestfunction-bedrock-model-read-access'
      - click 'Create policy'

```
* Repeat the above IAM UI interaction for the QAFunction lambda

* Create API Gateway
```
- browse to 'API Gateway' service
- find 'GenAIPrototype' API and click it
- click orange 'DeployAPI' button
- enter a 'Stage' name
- click 'Deploy'
```

-------------------
## Authentication and authorization

Adopt the approach as outlined in
* https://scriptingis.life/Cognito-AWS-SAM/
* https://github.com/scriptingislife/sam-cognito-example

## steps (from: https://scriptingis.life/Cognito-AWS-SAM/#authenticated-requests)
### Build / deploy
```bash
$ export COGNITO_USER_EMAIL='me@example.com'

$ sam build && sam deploy --parameter-overrides CognitoUserEmail=$COGNITO_USER_EMAIL
```
Make note of all of the outputs.

### First time sign-in
Check the inbox of $COGNITO_USER_EMAIL for a temporary password. This command will sign in for the first time.
```bash
$ aws cognito-idp initiate-auth \
   --auth-flow USER_PASSWORD_AUTH \
   --auth-parameters "USERNAME=$COGNITO_USER_EMAIL,PASSWORD=<TEMP-PASS>" \
   --client-id <CLIENT-ID> \
   --query "Session" \
   --output text \
   --region us-east-1
```
Use the output in the next command. This command will set a new password and provide the final token.
```bash
aws cognito-idp admin-respond-to-auth-challenge \
   --user-pool-id <USER-POOL> \
   --client-id <CLIENT-ID> \
   --challenge-responses "USERNAME=$COGNITO_USER_EMAIL,NEW_PASSWORD=<NEW-PASS>" \
   --challenge-name NEW_PASSWORD_REQUIRED \
   --session <SESSION> \
   --region us-east-1
```

Several tokens are provided. The ID Token is the one that will be sent with requests.

Now that we have set a new password, subsequent authentical flow / session establishment looks like the following:

```bash
$ aws cognito-idp initiate-auth \
   --auth-flow USER_PASSWORD_AUTH \
   --auth-parameters "USERNAME=$COGNITO_USER_EMAIL,PASSWORD=secret123" \
   --client-id $COGNITO_CLIENT_ID \
   --output json \
   --region us-east-1

{
    "ChallengeParameters": {},
    "AuthenticationResult": {
        "AccessToken": "eyJraWQiOiJBVU5zXC9ITVd2WXVDNURGVXB2ZHMwdUFpdjNqQWxDSHVrR2xzV1wvVGZvUkk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiI0MjRmYmIxNy00MTNkLTQ1NDQtYjhjZi01NDRlMGYwYjQ0MzkiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9iYzlUMHZvMTMiLCJjbGllbnRfaWQiOiI2Z29kOWN1c2tvbGpwbW9taWlmZnRoY3E0biIsIm9yaWdpbl9qdGkiOiIyOWVlNzJlOS04MGY3LTQxZmEtOGFhMC1iZjUzMTE0NzdlYTciLCJldmVudF9pZCI6ImE5ZmNiMTE3LTg4MzEtNGU0Ni04ZGMwLTcxZjQ3ZWQ5YzA5NyIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3MDEyMDQ3NzAsImV4cCI6MTcwMTIwODM3MCwiaWF0IjoxNzAxMjA0NzcwLCJqdGkiOiI3MWQ0YTc5NS1jODUwLTQxZGUtYjIyMC00YzBjMzhjMTk1YjciLCJ1c2VybmFtZSI6IjQyNGZiYjE3LTQxM2QtNDU0NC1iOGNmLTU0NGUwZjBiNDQzOSJ9.FnI_0ea-Wf0KdggLkvsPxLpyQBOgOH5C_imiuDkJy0gPGul3rKghPqPMfS1Y7zhi_d-HORaRF0qqSVGOqu5MGDA0mflobq6RBDNZF5yxa3Egt4fASjgfotBhVuRdmXjpmjyyQgtzerIuDiTjOf7WsQ7kmXf8rh5qs4hKnLabDe6g3mONgIAbt8xn45PkVT4LkkCSd2CgcXvCRiMx9iFNTICTKSKZXeCnnQXWF4OC432kNb2lXT5EZ82A3JLmeW9lh8-JN7j8g_DnS-ahqWiHwbdkBj1y1cvFpMbfPnKPFbaCUusx9Ex_A_t9EbCebhrXGxZ-LfrUxbHn2nCczOnCgg",
        "ExpiresIn": 3600,
        "TokenType": "Bearer",
        "RefreshToken": "eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.X-9fZ99PWzpSOdzmVqiUk7vQAeCpLNQyN0wb8uBTsd7G0jTnK-JzhyORHFtI5igjFBZbNs5pjo_4iJmXwNkFA_sjtUXR0vqqd6w_8AzULPvmsykAR3TGgPuaDDUaDGF8A4-vXr5OyTbYzKxxmx4B61z0pT3Eoavl5ElzSg6gy4PbDXiZTND3_DZpjM4NUQFR_bs5db5W6JpXQYkEYNSK7B5JQh8h0Voe3aHWHwiDcl4F1hecb5Hl3kmLdAZWyCYpR4yvmyZMrIfGR2ncZp7x9qsZGdU6VcLC28xVq048Owd-xVRt-7Ty0bWPdFt2ZkZMPf4Dnr5_6Ya7snZl1hozfQ.RKK7TVNFwtyqd7Tc.qpM59UQVA4nkYFcCldjqcPH51Wgbghq2C2wnnsL6ioDNXCdGvkQrCqqQTIevDbgukajqClc6NGVLrO1QNBX2xENj5wxXifUFDoHIUdyIgwtZJB4kVsDAPxHAB3Dz0SZIqkdE0qHumhSKpiblOegN5SrcGt72n22u_tcJpvMX7YfHikUO9EbuLSWwLb9vXtMa22Ie-v_tQOyr33ZD3hIZ5k_SjK5CcV2-CAE9fIigwljJJsv1riS1AON3KhUtmavtWM1PQ829XhzMSM8TKF5crUpkG1Tb04Zsg1NVKERaoAjCyaKOjMJHSkDkigN3_m5ZNIz58BVD6DMidLB0zUR1Faig1T4wAwPJTUTWg0s5siTCZ-jNri2i7v7KAeVb45R0jjRhTrhxguRUbZLAKmY3iuAs62JataArm09NL6zqeIzPKsqoEV3suFchTfxBGGGZq9rHn_piqNgoC3aytyw-HHe4xJVnbEW9VMRgnQDWv4ORd8yBuEPYzQ_J2vFfW_9vQ3vfCmZ8cRo2IZGPo1xbhIrSQsdb_500nZwjuUbsmX8ZDyXcuQyf6dbm9RpYOP5Vt3dn1FRiT9_Hp7C1h5H_B12v9QLnFHBhwHDSqkYQfv_96XCdgnavnBlZpHlDbVhV3z0cBKWTPLXKUds5vIOKJtqgLutXuwKE7p9_zQPEImpjcyKJAgnv3B2HQg78QdL_nkz33WS01llI3MVXeUjVClci3jiZ9FwY6Z0bLI-z6ZPGak28q13peAS6jwq-L7lJnL_O7jc0bg4XdSP0PZCRc1CmoaG026P5JhymwQBI1IyOVtXMMIqbqSUSDYwaSLihasI_waECH3Pc7L-UuRMNnfcA9tHO31lBqRGwWnEcqYWnKK3bdxu0ItaK-NCmRDt5zCsu3oxVl0mOm2w2Vh32wuSzuxebXsTBDzlZjmhaQmL7OQOzKrxXCi4mpg725bz9dCzbK2T7v6xP40chofdgKjyTFlyLcXng-QFZ9LoY8vEQGS3OmcXpIPA__Mndmh09Eemr6T_7n2c237-n-BmJvif7HlpLRxb26xlF79QMC3iItzgnO0WQHW9TEzX5zW9SRxY5SgRv_0F8B1KZfece2AuQlnLmZoHKHLVeRouYYQqFQJJx1UlUbYqtghUL52QCOcOl7CYyW1KcqxEjAwQZyXuotWEz8PmPLLgN6OjjDkJ67GeEPBtW6uXSyDv4OZhTtnv_TzwZmEqQ7R5G0vT5Dces7naI6xJZnEo-oysXvA7gtpS-WBBJhqYOKF-9RaI4SJZMgqrxKy7US75ph3w3B9-6ltm-TgqIow2UL3ZZ_fBKZXXht3hYMgIBDx-qX59k._RULKmkEswevZEDS4lIaJg",
        "IdToken": "eyJraWQiOiJGa3FyRldNQlF5OHhiQzZXODByeHdNYTVXRDRyUFFIM2IxTXptNjJRK1pnPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI0MjRmYmIxNy00MTNkLTQ1NDQtYjhjZi01NDRlMGYwYjQ0MzkiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9iYzlUMHZvMTMiLCJjb2duaXRvOnVzZXJuYW1lIjoiNDI0ZmJiMTctNDEzZC00NTQ0LWI4Y2YtNTQ0ZTBmMGI0NDM5Iiwib3JpZ2luX2p0aSI6IjI5ZWU3MmU5LTgwZjctNDFmYS04YWEwLWJmNTMxMTQ3N2VhNyIsImF1ZCI6IjZnb2Q5Y3Vza29sanBtb21paWZmdGhjcTRuIiwiZXZlbnRfaWQiOiJhOWZjYjExNy04ODMxLTRlNDYtOGRjMC03MWY0N2VkOWMwOTciLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTcwMTIwNDc3MCwiZXhwIjoxNzAxMjA4MzcwLCJpYXQiOjE3MDEyMDQ3NzAsImp0aSI6IjI1MjJkZmVjLTA1ZjUtNDkxZC05MjAyLWI0YmM5ODBhMDgxNCIsImVtYWlsIjoiZWRnYXIuaG9uaW5nQGFoZWFkLmNvbSJ9.pxZ1XUEEc6uUJB5LtYcnoAI1eFHKRWsUZxaN-ufrJM_0JMf9IparCKNKw_Loq5AzDt7gh7Vy-f3CrdfWRvwxaqJW41TSCb9Yt_NUlbwK6O8NizxD6109fSnDhIFa-QjRE_H9Q2ar-yY5Fvp52PG3kVLlvdZ_rbRSraKKMb6GbDOJJv2JtvPkD5eDmgkynMUvC0gTbEEDy09HZ9LAkC3nfm1S7CzemAO6xO0qlPyVjWPUPYz8XFHrO8XNLGWljyDzB66mMRq93u3pLUuUM0KBQ5wTqyj0TuLSSkCT1R9zS7KRHJ6eZ4rklsNgCq9dnZPhxVFzzE5BBSzN7xgpgw7UWA"
    }
}

$ export COGNITO_ID_TOKEN="eyJraWQiOiJGa3FyRldNQlF5OHhiQzZXODByeHdNYTVXRDRyUFFIM2IxTXptNjJRK1pnPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI0MjRmYmIxNy00MTNkLTQ1NDQtYjhjZi01NDRlMGYwYjQ0MzkiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9iYzlUMHZvMTMiLCJjb2duaXRvOnVzZXJuYW1lIjoiNDI0ZmJiMTctNDEzZC00NTQ0LWI4Y2YtNTQ0ZTBmMGI0NDM5Iiwib3JpZ2luX2p0aSI6IjI5ZWU3MmU5LTgwZjctNDFmYS04YWEwLWJmNTMxMTQ3N2VhNyIsImF1ZCI6IjZnb2Q5Y3Vza29sanBtb21paWZmdGhjcTRuIiwiZXZlbnRfaWQiOiJhOWZjYjExNy04ODMxLTRlNDYtOGRjMC03MWY0N2VkOWMwOTciLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTcwMTIwNDc3MCwiZXhwIjoxNzAxMjA4MzcwLCJpYXQiOjE3MDEyMDQ3NzAsImp0aSI6IjI1MjJkZmVjLTA1ZjUtNDkxZC05MjAyLWI0YmM5ODBhMDgxNCIsImVtYWlsIjoiZWRnYXIuaG9uaW5nQGFoZWFkLmNvbSJ9.pxZ1XUEEc6uUJB5LtYcnoAI1eFHKRWsUZxaN-ufrJM_0JMf9IparCKNKw_Loq5AzDt7gh7Vy-f3CrdfWRvwxaqJW41TSCb9Yt_NUlbwK6O8NizxD6109fSnDhIFa-QjRE_H9Q2ar-yY5Fvp52PG3kVLlvdZ_rbRSraKKMb6GbDOJJv2JtvPkD5eDmgkynMUvC0gTbEEDy09HZ9LAkC3nfm1S7CzemAO6xO0qlPyVjWPUPYz8XFHrO8XNLGWljyDzB66mMRq93u3pLUuUM0KBQ5wTqyj0TuLSSkCT1R9zS7KRHJ6eZ4rklsNgCq9dnZPhxVFzzE5BBSzN7xgpgw7UWA"
```

We can now use the 'id token' to access the lambdas as exposed by the API gateway as in the following examples:

```bash
$ curl -H "Authorization: Bearer $COGNITO_ID_TOKEN" https://n2kqilxd7g.execute-api.us-east-1.amazonaws.com/api/qa

{"message": "Please provide a query in your request payload"}
```

```bash
$ curl \
  -H "Authorization: Bearer $COGNITO_ID_TOKEN" \
  "https://n2kqilxd7g.execute-api.us-east-1.amazonaws.com/api/qa?mode=single_shot&show_sources=True&query=what+is+Agda"

{"question": "what is Agda", "answer": " Agda is a proof assistant created by Ulf Norell at Chalmers University of Technology. It is designed for programming and verifying functional programs, with an emphasis on inductive and recursively defined data types. Proofs in Agda are written as part of the program itself, using dependent types.\n\n", "source_documents": [{"page_content": "Verified Functional\nProgramming in Agda", "source": "verified-functional-programming-in-agda.pdf"}, {"page_content": "Agda User Manual, Release 2.6.5\n4 Chapter 1. Overview", "source": "agda-readthedocs-io-en-latest.pdf"}, {"page_content": "Agda User Manual, Release 2.6.5\n298 Bibliography", "source": "agda-readthedocs-io-en-latest.pdf"}, {"page_content": "Agda User Manual, Release 2.6.5\nCONTENTS 1", "source": "agda-readthedocs-io-en-latest.pdf"}]}
```


## Creating new users / accounts in AWS Cognito

Using the aws CLI tool:

```bash
aws cognito-idp sign-up \
    --region us-east-1 \
    --client-id  $ COGNITO_CLIENT_ID\
    --username <new user's email address> \
    --password <new user's password>
```

Alternatively, a new user can be introduced via Amazon Cognito's web UI, navigating to 'Users' section in the appropriate User pool's page.

Either the user can go through a workflow to "confirm" their email address, or the new user's confirmation status can be modfied through Amazon Cognito's web UI but navigating to the 'User pool', 
selecting the new user's entry in the 'Users' list, selecting 'Edit User' and mark their email address as 'confirmed'

## Troubleshooting hints

* varifying the validity of a Cognito 'id token' can be done by navigating to the appropriate 'API Gateway' entry, selecting the 'Authorizers' view in the left marging, followed by selecting thr 'CognitoAuthorizer'.
This in turn shows a 'Test authorizer', allowing the 'Token value' (Cognito IdToken) to be entered. (Note: make sure NOT to add enclosing double quote values). A successful test will result in a '200' result with 
a 'Claims' section in JSON format, containing key information on the user's email address, token expiration date/time stamp, etc.
 
 
-------------------
## Session mamagement implementation

Note that full event details as currently logged by our authenticated lambdas provide insight into what properties are potentially avaiable to base the concept of a 'convernsation session' on.
Below an example log message from the QAFunction:

```
[INFO]	2023-11-28T22:43:55.987Z	5c13d982-3b13-4a94-acda-ed57dfd54c3e	=== full event details: ===
{'resource': '/qa', 'path': '/qa', 'httpMethod': 'GET', 'headers': {'Accept': '*/*', 
'Authorization': 'Bearer eyJraWQiOiJGa3FyRldNQlF5OHhiQzZXODByeHdNYTVXRDRyUFFIM2IxTXptNjJRK1pnPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI0MjRmYmIxNy00MTNkLTQ1NDQtYjhjZi01NDRlMGYwYjQ0MzkiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9iYzlUMHZvMTMiLCJjb2duaXRvOnVzZXJuYW1lIjoiNDI0ZmJiMTctNDEzZC00NTQ0LWI4Y2YtNTQ0ZTBmMGI0NDM5Iiwib3JpZ2luX2p0aSI6IjExODI4NTkxLTcyMGQtNGE4MS05ZDc5LTg5MzQ0MDY5ZDFiYSIsImF1ZCI6IjZnb2Q5Y3Vza29sanBtb21paWZmdGhjcTRuIiwiZXZlbnRfaWQiOiJjMTNkNDExZi1mYjQ2LTQ4ZWEtOTE4OC02OGYzOTAxODgwNTAiLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTcwMTIwOTQxOCwiZXhwIjoxNzAxMjEzMDE4LCJpYXQiOjE3MDEyMDk0MTgsImp0aSI6IjA5MWMwZTA1LWFmNGEtNDhiYi04MGRkLTY3YWJlNWM2ZjRkZCIsImVtYWlsIjoiZWRnYXIuaG9uaW5nQGFoZWFkLmNvbSJ9.neEEX9ZafVLupm30a8wPESitqlu6JBHovH0x8SaIrlhW8H-vgb5qcUKLAJX6vGaSxD_5nQ6kDd-uyHPfkwXLBuEzFYluVmqUEvGPQtVTQVKBwZpDH6fcXlB_e0lb-62ybTg2t-kn7QvR5z49DOhPFYMueFiNUMfFoM23P5edVAbO8SHlMLVl6iKGhSJnTXlDNxvvye04q1ZrdwgsRPI6P2nBQPcJdTK16nM0uYaiVSnEzwUP8LpS8ePVNK2d9pg74hmCDa71D07fTsTauSyqm4PtArMCZk2PJXdtS6uk59nooTs4p8WI_o_7ViVdPxQZQ-H7OAm4kYI7IdB03IhHTQ', 
'CloudFront-Forwarded-Proto': 'https', 'CloudFront-Is-Desktop-Viewer': 'true', 'CloudFront-Is-Mobile-Viewer': 'false', 
'CloudFront-Is-SmartTV-Viewer': 'false', 'CloudFront-Is-Tablet-Viewer': 'false', 'CloudFront-Viewer-ASN': '16509', 'CloudFront-Viewer-Country': 'US',
'Host': 'n2kqilxd7g.execute-api.us-east-1.amazonaws.com', 'User-Agent': 'curl/8.3.0', 'Via': '2.0 f5c01ee1bc998fcfadde7a8a989805a6.cloudfront.net (CloudFront)', 
'X-Amz-Cf-Id': '5XtFQbq6qMy25XLJk4EYK0AyEH5lW4PeYd2E9h1-VZ8JOxltcmtEcw==', 'X-Amzn-Trace-Id': 'Root=1-65666d25-7a86529b13a067146d9ada5f', 
'X-Forwarded-For': '18.191.141.21, 15.158.61.197', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'Accept': ['*/*'], 
'Authorization': ['Bearer eyJraWQiOiJGa3FyRldNQlF5OHhiQzZXODByeHdNYTVXRDRyUFFIM2IxTXptNjJRK1pnPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI0MjRmYmIxNy00MTNkLTQ1NDQtYjhjZi01NDRlMGYwYjQ0MzkiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9iYzlUMHZvMTMiLCJjb2duaXRvOnVzZXJuYW1lIjoiNDI0ZmJiMTctNDEzZC00NTQ0LWI4Y2YtNTQ0ZTBmMGI0NDM5Iiwib3JpZ2luX2p0aSI6IjExODI4NTkxLTcyMGQtNGE4MS05ZDc5LTg5MzQ0MDY5ZDFiYSIsImF1ZCI6IjZnb2Q5Y3Vza29sanBtb21paWZmdGhjcTRuIiwiZXZlbnRfaWQiOiJjMTNkNDExZi1mYjQ2LTQ4ZWEtOTE4OC02OGYzOTAxODgwNTAiLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTcwMTIwOTQxOCwiZXhwIjoxNzAxMjEzMDE4LCJpYXQiOjE3MDEyMDk0MTgsImp0aSI6IjA5MWMwZTA1LWFmNGEtNDhiYi04MGRkLTY3YWJlNWM2ZjRkZCIsImVtYWlsIjoiZWRnYXIuaG9uaW5nQGFoZWFkLmNvbSJ9.neEEX9ZafVLupm30a8wPESitqlu6JBHovH0x8SaIrlhW8H-vgb5qcUKLAJX6vGaSxD_5nQ6kDd-uyHPfkwXLBuEzFYluVmqUEvGPQtVTQVKBwZpDH6fcXlB_e0lb-62ybTg2t-kn7QvR5z49DOhPFYMueFiNUMfFoM23P5edVAbO8SHlMLVl6iKGhSJnTXlDNxvvye04q1ZrdwgsRPI6P2nBQPcJdTK16nM0uYaiVSnEzwUP8LpS8ePVNK2d9pg74hmCDa71D07fTsTauSyqm4PtArMCZk2PJXdtS6uk59nooTs4p8WI_o_7ViVdPxQZQ-H7OAm4kYI7IdB03IhHTQ'], 
'CloudFront-Forwarded-Proto': ['https'], 'CloudFront-Is-Desktop-Viewer': ['true'], 'CloudFront-Is-Mobile-Viewer': ['false'], 
'CloudFront-Is-SmartTV-Viewer': ['false'], 'CloudFront-Is-Tablet-Viewer': ['false'], 'CloudFront-Viewer-ASN': ['16509'], 'CloudFront-Viewer-Country': ['US'], 
'Host': ['n2kqilxd7g.execute-api.us-east-1.amazonaws.com'], 'User-Agent': ['curl/8.3.0'], 'Via': ['2.0 f5c01ee1bc998fcfadde7a8a989805a6.cloudfront.net (CloudFront)'], 
'X-Amz-Cf-Id': ['5XtFQbq6qMy25XLJk4EYK0AyEH5lW4PeYd2E9h1-VZ8JOxltcmtEcw=='], 'X-Amzn-Trace-Id': ['Root=1-65666d25-7a86529b13a067146d9ada5f'], 
'X-Forwarded-For': ['18.191.141.21, 15.158.61.197'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 
'queryStringParameters': {'mode': 'single_shot', 'query': 'what is Agda', 'show_sources': 'True'}, 
'multiValueQueryStringParameters': {'mode': ['single_shot'], 'query': ['what is Agda'], 'show_sources': ['True']}, 
'pathParameters': None, 'stageVariables': None, 'requestContext': {'resourceId': 'yygk3d', 
'authorizer': {'claims': {'origin_jti': '11828591-720d-4a81-9d79-89344069d1ba', 'sub': '424fbb17-413d-4544-b8cf-544e0f0b4439', 'aud': '6god9cuskoljpmomiiffthcq4n', 
'event_id': 'c13d411f-fb46-48ea-9188-68f390188050', 'token_use': 'id', 'auth_time': '1701209418', 
'iss': 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_bc9T0vo13', 'cognito:username': '424fbb17-413d-4544-b8cf-544e0f0b4439', 'exp': 'Tue Nov 28 23:10:18 UTC 2023', 
'iat': 'Tue Nov 28 22:10:18 UTC 2023', 'jti': '091c0e05-af4a-48bb-80dd-67abe5c6f4dd', 'email': 'edgar.honing@ahead.com'}}, 'resourcePath': '/qa', 
'httpMethod': 'GET', 'extendedRequestId': 'PIX98E6noAMEhpQ=', 'requestTime': '28/Nov/2023:22:43:49 +0000', 'path': '/api/qa', 'accountId': '784947213393', 
'protocol': 'HTTP/1.1', 'stage': 'api', 'domainPrefix': 'n2kqilxd7g', 'requestTimeEpoch': 1701211429791, 'requestId': '39c2f069-16e9-4479-abc6-fefb74fbd3ae', 
'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '18.191.141.21', 'principalOrgId': None, 'accessKey': None, 
'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'curl/8.3.0', 'user': None}, 
'domainName': 'n2kqilxd7g.execute-api.us-east-1.amazonaws.com', 'apiId': 'n2kqilxd7g'}, 'body': None, 'isBase64Encoded': False}
```

in 'pretty printed' layout (replacing the actual long token values with just '\<TOKEN VALUE\>'):

```
{
  "resource": "/qa",
  "path": "/qa",
  "httpMethod": "GET",
  "headers": {
    "Accept": "*/*",
    "Authorization": "Bearer <TOKEN VALUE>",
    "CloudFront-Forwarded-Proto": "https",
    "CloudFront-Is-Desktop-Viewer": "true",
    "CloudFront-Is-Mobile-Viewer": "false",
    "CloudFront-Is-SmartTV-Viewer": "false",
    "CloudFront-Is-Tablet-Viewer": "false",
    "CloudFront-Viewer-ASN": "16509",
    "CloudFront-Viewer-Country": "US",
    "Host": "n2kqilxd7g.execute-api.us-east-1.amazonaws.com",
    "User-Agent": "curl/8.3.0",
    "Via": "2.0 f5c01ee1bc998fcfadde7a8a989805a6.cloudfront.net (CloudFront)",
    "X-Amz-Cf-Id": "5XtFQbq6qMy25XLJk4EYK0AyEH5lW4PeYd2E9h1-VZ8JOxltcmtEcw==",
    "X-Amzn-Trace-Id": "Root=1-65666d25-7a86529b13a067146d9ada5f",
    "X-Forwarded-For": "18.191.141.21, 15.158.61.197",
    "X-Forwarded-Port": "443",
    "X-Forwarded-Proto": "https"
  },
  "multiValueHeaders": {
    "Accept": [
      "*/*"
    ],
    "Authorization": [
      "Bearer <TOKEN VALUE>"
    ],
    "CloudFront-Forwarded-Proto": [
      "https"
    ],
    "CloudFront-Is-Desktop-Viewer": [
      "true"
    ],
    "CloudFront-Is-Mobile-Viewer": [
      "false"
    ],
    "CloudFront-Is-SmartTV-Viewer": [
      "false"
    ],
    "CloudFront-Is-Tablet-Viewer": [
      "false"
    ],
    "CloudFront-Viewer-ASN": [
      "16509"
    ],
    "CloudFront-Viewer-Country": [
      "US"
    ],
    "Host": [
      "n2kqilxd7g.execute-api.us-east-1.amazonaws.com"
    ],
    "User-Agent": [
      "curl/8.3.0"
    ],
    "Via": [
      "2.0 f5c01ee1bc998fcfadde7a8a989805a6.cloudfront.net (CloudFront)"
    ],
    "X-Amz-Cf-Id": [
      "5XtFQbq6qMy25XLJk4EYK0AyEH5lW4PeYd2E9h1-VZ8JOxltcmtEcw=="
    ],
    "X-Amzn-Trace-Id": [
      "Root=1-65666d25-7a86529b13a067146d9ada5f"
    ],
    "X-Forwarded-For": [
      "18.191.141.21, 15.158.61.197"
    ],
    "X-Forwarded-Port": [
      "443"
    ],
    "X-Forwarded-Proto": [
      "https"
    ]
  },
  "queryStringParameters": {
    "mode": "single_shot",
    "query": "what is Agda",
    "show_sources": "True"
  },
  "multiValueQueryStringParameters": {
    "mode": [
      "single_shot"
    ],
    "query": [
      "what is Agda"
    ],
    "show_sources": [
      "True"
    ]
  },
  "pathParameters": "None",
  "stageVariables": "None",
  "requestContext": {
    "resourceId": "yygk3d",
    "authorizer": {
      "claims": {
        "origin_jti": "11828591-720d-4a81-9d79-89344069d1ba",
        "sub": "424fbb17-413d-4544-b8cf-544e0f0b4439",
        "aud": "6god9cuskoljpmomiiffthcq4n",
        "event_id": "c13d411f-fb46-48ea-9188-68f390188050",
        "token_use": "id",
        "auth_time": "1701209418",
        "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_bc9T0vo13",
        "cognito:username": "424fbb17-413d-4544-b8cf-544e0f0b4439",
        "exp": "Tue Nov 28 23:10:18 UTC 2023",
        "iat": "Tue Nov 28 22:10:18 UTC 2023",
        "jti": "091c0e05-af4a-48bb-80dd-67abe5c6f4dd",
        "email": "edgar.honing@ahead.com"
      }
    },
    "resourcePath": "/qa",
    "httpMethod": "GET",
    "extendedRequestId": "PIX98E6noAMEhpQ=",
    "requestTime": "28/Nov/2023:22:43:49 +0000",
    "path": "/api/qa",
    "accountId": "784947213393",
    "protocol": "HTTP/1.1",
    "stage": "api",
    "domainPrefix": "n2kqilxd7g",
    "requestTimeEpoch": 1701211429791,
    "requestId": "39c2f069-16e9-4479-abc6-fefb74fbd3ae",
    "identity": {
      "cognitoIdentityPoolId": "None",
      "accountId": "None",
      "cognitoIdentityId": "None",
      "caller": "None",
      "sourceIp": "18.191.141.21",
      "principalOrgId": "None",
      "accessKey": "None",
      "cognitoAuthenticationType": "None",
      "cognitoAuthenticationProvider": "None",
      "userArn": "None",
      "userAgent": "curl/8.3.0",
      "user": "None"
    },
    "domainName": "n2kqilxd7g.execute-api.us-east-1.amazonaws.com",
    "apiId": "n2kqilxd7g"
  },
  "body": "None",
  "isBase64Encoded": "False"
}
```

Note the value of the leaf at path 'requestContext->authorizer->claims->cognito:username' and 'requestContext->authorizer->claims->sub' have value "424fbb17-413d-4544-b8cf-544e0f0b4439", which matches the user name of the user in 'MyUserPool' in Amazon Cognito.

As per the [Cognito developerguide](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-id-token.html), this uniquely identifies the user and will serve as our 'session id'. (Note that this means that we only allow a single session per user)


We implement 'session' management as follows:
* in the ***QAFunction*** python file (**qa/invoke.py**), pass the value of event['requestContext->authorizer->claims->sub'] as the 'session_id' to 'handle_query'
* in **utils_layer/query_handler_api.py**, pass session id on to qa handlers
* conv qa handler implementation(s) can use session id to keep an unique ***ConversationalRetrievalChain*** per session, as each will need its own conversation_memory instance.
* resetting a conversation implies reinstantiating a conversation_memory instance are recreating the session's ***ConversationalRetrievalChain*** instance

-------------------
## Custom fixes
* in an attempt to perform Pinecone embedding inserts synchronously (to avoid threadpool spinup that is not allowed in AWS Lambda) the following mod was made:
in file **libs-layer/python/langchain/vectorstores/pinecone.py**:   lines 139-160: async_req=False, and no async results collection


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Deploy the sample application

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3 installed](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build --use-container
sam deploy --guided
```

The first command will build the source of your application. The second command will package and deploy your application to AWS, with a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modifies IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

You can find your API Gateway Endpoint URL in the output values displayed after deployment.

## Use the SAM CLI to build and test locally

Build your application with the `sam build --use-container` command.

```bash
sam-genai-rag-prototype$ sam build --use-container
```

The SAM CLI installs dependencies defined in `sam-genai-rag-prototype/requirements.txt`, creates a deployment package, and saves it in the `.aws-sam/build` folder.

Test a single function by invoking it directly with a test event. An event is a JSON document that represents the input that the function receives from the event source. Test events are included in the `events` folder in this project.

Run functions locally and invoke them with the `sam local invoke` command.

```bash
sam-genai-rag-prototype$ sam local invoke HelloWorldFunction --event events/event.json
```

The SAM CLI can also emulate your application's API. Use the `sam local start-api` to run the API locally on port 3000.

```bash
sam-genai-rag-prototype$ sam local start-api
sam-genai-rag-prototype$ curl http://localhost:3000/
```

The SAM CLI reads the application template to determine the API's routes and the functions that they invoke. The `Events` property on each function's definition includes the route and method for each path.

```yaml
      Events:
        QA:
          Type: Api
          Properties:
            Path: /qa
            Method: get
            RestApiId: !Ref AppApi
            Auth:
              Authorizer: CognitoAuthorizer
```

## Add a resource to your application
The application template uses AWS Serverless Application Model (AWS SAM) to define application resources. AWS SAM is an extension of AWS CloudFormation with a simpler syntax for configuring common serverless application resources such as functions, triggers, and APIs. For resources not included in [the SAM specification](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md), you can use standard [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html) resource types.

## Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
sam-genai-rag-prototype$ sam logs -n QAFunction --stack-name "sam-genai-rag-prototype" --tail
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

## Unit tests

Tests are defined in the `tests` folder in this project. Use PIP to install the [pytest](https://docs.pytest.org/en/latest/) and run unit tests.

```bash
sam-genai-rag-prototype$ pip install pytest pytest-mock --user
sam-genai-rag-prototype$ python -m pytest tests/ -v
```

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
sam delete --stack-name "sam-genai-rag-prototype"
```

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)
