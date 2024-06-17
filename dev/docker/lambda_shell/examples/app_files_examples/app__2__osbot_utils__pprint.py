from osbot_utils.utils.Dev import pprint


def lambda_handler(event, context):
    pprint('(now using osbot_utils api -  from inside the lambda functions')
    return {
        'statusCode': 200,
        'body'      : "it's 42 of course"
    }
