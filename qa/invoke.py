import json

# lambda layer usage experiment
from bedrock import get_bedrock_client
from doc_handler import *


bedrock_client = get_bedrock_client(runtime=False)


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    txt_from_layer = handle_doc()
    txt_bedrock_client = str(bedrock_client)
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"hello world + {txt_from_layer} + {txt_bedrock_client}",
            # "location": ip.text.replace("\n", "")
        }),
    }
