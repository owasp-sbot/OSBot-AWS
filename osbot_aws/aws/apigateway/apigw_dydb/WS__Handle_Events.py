from osbot_aws.aws.apigateway.apigw_dydb.WS__DyDB           import WS__DyDB
from osbot_aws.aws.apigateway.apigw_dydb.WS__Handle_Lambda  import WS__Handle_Lambda


class WS__Handle_Events(WS__Handle_Lambda):
    dydb_ws    : WS__DyDB
    source     : str        = 'WS__Handle_Events'


    def route__connect(self, event, connection_id):
        kwargs   = dict(connection_id = connection_id ,
                        source        = self.source   ,
                        lambda_event  = event         )
        self.dydb_ws.register_connection(**kwargs)
        return {'statusCode': 200, 'body': 'Connected.'}

    def route_default(self, event, connection_id):
        kwargs   = dict(connection_id = connection_id ,
                        source        = self.source   ,
                        lambda_event  = event         )
        return self.dydb_ws.handle_route(**kwargs)

    def route_disconnect(self, event, connection_id):
        kwargs   = dict(connection_id = connection_id ,
                        source        = self.source   ,
                        lambda_event  = event         )
        self.dydb_ws.register_disconnect(**kwargs)
        return {'statusCode': 200, 'body': 'Disconnected.'}

