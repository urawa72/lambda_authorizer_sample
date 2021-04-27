import base64
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    logger.debug(event)

    claims = event['requestContext']['authorizer']['claims']
    claims = base64.b64decode(claims)
    claims = json.loads(claims)
    logger.debug(claims)
    logger.debug(json.dumps(claims))

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Methods': '*',
            # 'Access-Control-Allow-Credentials': 'true',
        },
        'body': json.dumps({'result': 'hello world!'})
    }
