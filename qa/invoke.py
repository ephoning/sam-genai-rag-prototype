import json
import logging

from query_handler_api import handle_query

logger = logging.getLogger()
logger.setLevel(logging.INFO)



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
    log_info += "=== full event details: ===\n"
    log_info += f"{event}\n"
    logger.info(log_info)
    
    
    query = event.get("query")
    
    if not query:
        response = dict(message="Please provide a query in yuor request payload")
    else:
        mode = event.get("mode", "conversation"). # options: ["conversation", "single shot"]
        reset_conversation = event.get("reset_conversation")
        reset_conversation = True if reset_conversation in ["True", "true", "T", "t"] else False
        show_sources = event.get("show_sources")
        show_sources = True if show_sources in ["True", "true", "T", "t"] else False
        session_id = event.get("session_id", "public")
    
        response = handle_query(dict(session_id=session_id, mode=mode, query=query, reset_conversation=reset_conversation))

    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }
