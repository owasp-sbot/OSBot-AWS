# invoke using curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'

def lambda_handler(event, context):
    print('From inside the lambda functions')
    return {
        'statusCode': 200,
        'body'      : 'Hello there'
    }
