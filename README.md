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

-------------------
# Authenticaion and athorization

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
   --output text
```
Use the output in the next command. This command will set a new password and provide the final token.
```bash
aws cognito-idp admin-respond-to-auth-challenge \
   --user-pool-id <USER-POOL> \
   --client-id <CLIENT-ID> \
   --challenge-responses "USERNAME=$COGNITO_USER_EMAIL,NEW_PASSWORD=<NEW-PASS>" \
   --challenge-name NEW_PASSWORD_REQUIRED \
   --session <SESSION>
```
Several tokens are provided. The ID Token is the one that will be sent with requests.
### Authneticated requests
The provided token can be sent in the *Authorization* header of each request. For example:
```
curl -H "Authorization: Bearer <ID-TOKEN>" https://<API-ID>.execute-api.us-east-1.amazonaws.com/api/qa/ \
   -H 'content-type: application/json' \
   -d '{"mode": "single_short", "query": "what is Agda?", "show_sources": "True"}'
```

-------------------
# Custom fixes
* in an attempt to perform Pinecone embedding inserts synchronously (to avoid threadpool spinup that is not allowed in AWS Lambda) the following mod was made:
** in file libs-layer/python/langchain/vectorstores/pinecone.py:   lines 139-160: async_req=False, and no asyn results collection

-------------------

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
