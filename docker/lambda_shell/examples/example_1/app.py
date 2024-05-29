from osbot_aws.aws.sts.STS import STS
from osbot_utils.utils.Dev import pprint


def lambda_handler(event, context):
    pprint('now using osbot-utils - from inside the lambda functions')
    sts = STS()
    current_identity = sts.caller_identity()
    body             = f'Hi, the current identity is {current_identity}'
    return {
        'statusCode': 200,
        'body'      : body
    }
