from osbot_aws.aws.apigateway.apigw_dydb.WS__Handle_Events import WS__Handle_Events

ws_handle_events = WS__Handle_Events()

def run(event, context):
    return ws_handle_events.handle_lambda(event, context)

