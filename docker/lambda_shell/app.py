# invoke using
#        curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'

from osbot_aws.apis.shell.Lambda_Shell import lambda_shell

@lambda_shell
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body'      : 'this is not from lambda shell'
    }
