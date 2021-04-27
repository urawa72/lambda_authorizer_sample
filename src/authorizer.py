import base64
import json
import logging
import os
import re
from typing import Dict, Optional
from urllib.request import urlopen

from jose import jwt

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

domain = os.getenv('AUTH0_DOMAIN')
jwks_url = f'https://{domain}/.well-known/jwks.json'
issuer = f'https://{domain}/'
audience = os.getenv('AUTH0_AUDIENCE')


def lambda_handler(event: Dict, context: Dict) -> Optional[Dict]:
    logger.info(event)
    result = verify(event)
    logger.debug(result)
    return result


def verify(event: Dict) -> Optional[Dict]:
    resource = event['methodArn']

    try:
        token = get_token(event)

        rsa_key = get_rsa_key(token)

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms='RS256',
            audience=audience,
            issuer=issuer
        )

        logger.debug(payload)
        return generate_policy('*', 'Allow', resource, payload)
    except Exception as error:
        logger.error(error)
        return generate_policy('*', 'Deny', resource, None)


def get_token(event: Dict) -> str:
    return re.match(r'^Bearer (.*)$', event['authorizationToken']).groups()[0]


def get_rsa_key(token: str) -> Optional[Dict]:
    jsonurl = urlopen(jwks_url)
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
            return rsa_key


def generate_policy(
        principal_id: str, effect: str, resource: str, payload: Optional[Dict]
        ) -> Dict:
    policy = {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': resource
                }
            ]
        }
    }

    if effect == 'Allow':
        json_context = json.dumps(payload)
        base64_context = base64.b64encode(json_context.encode('utf8'))
        policy['context'] = {'claims': base64_context.decode('utf-8')}

    return policy
