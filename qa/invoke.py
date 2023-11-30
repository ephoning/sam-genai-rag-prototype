import json
import logging
from typing import Any, Dict

from query_handler_api import handle_query

logger = logging.getLogger()
logger.setLevel(logging.INFO)


trues = ["True", "true", "T", "t"]


def get_params(event: Dict[str, Any]) -> Dict[str, Any]:
    params = None
    
    if event['httpMethod'] == "GET":
        params = event['queryStringParameters']
    
    if event['httpMethod'] == "POST":
        params =json.loads(event['body'])
        
    return params
    

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
    log_info = "=== full event details: ===\n"
    log_info += f"{event}\n"
    logger.info(log_info)
    
    params = get_params(event)
    
    if not params or not params.get("query"):
        response = dict(message="Please provide at least a query in your request")
    else:
        query = params.get("query")
        
        mode = params.get("mode", "conversation")  # options: ["conversation", "single_shot"]

        reset_conversation = params.get("reset_conversation")
        reset_conversation = True if reset_conversation in trues else False
        
        show_sources = params.get("show_sources")
        show_sources = True if show_sources in trues else False
        
        try:
            session_id = event['requestContext']['authorizer']['claims']['sub'] 
            logger.info(f"Got session id: {session_id}")
        except:
            logger.warn("Could not get 'session id' from event => using 'anonymous' session")
            session_id = 'anonymous'

        response = handle_query(dict(session_id=session_id, mode=mode, query=query, show_sources=show_sources, reset_conversation=reset_conversation))

    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }
