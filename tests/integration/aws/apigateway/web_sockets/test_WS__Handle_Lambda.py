from unittest import TestCase

from osbot_aws.aws.apigateway.apigw_dydb.WS__Handle_Lambda import WS__Handle_Lambda


class test_WS__Handle_Lambda(TestCase):
    ws_handle_lambda : WS__Handle_Lambda()
    @classmethod

    def setUpClass(cls):
        cls.ws_handle_lambda = WS__Handle_Lambda()

    def test_handle_lambda(self):
        connection_id   = 'an connection id'
        request_content = {'connectionId': connection_id}
        event           = {'requestContext': request_content}
        context         = None
        with self.ws_handle_lambda as _:

            # unknown route
            route_key                   = 'unknown_route'
            request_content['routeKey'] = route_key
            result_route_route          = _.handle_lambda(event, context)
            assert result_route_route     == {'body': 'Route not recognized.', 'statusCode': 400}

            # connect route
            route_key                   = '$connect'
            request_content['routeKey'] = route_key
            result_route_route          = _.handle_lambda(event, context)
            assert result_route_route     == {'body': 'Connected.', 'statusCode': 200}

            # disconnect route
            route_key                   = '$disconnect'
            request_content['routeKey'] = route_key
            result_route_route          = _.handle_lambda(event, context)
            assert result_route_route     == {'body': 'Disconnected.', 'statusCode': 200}

            # default route
            route_key                   = '$default'
            request_content['routeKey'] = route_key
            result_route_route          = _.handle_lambda(event, context)
            assert result_route_route          == {'body': 'Message received on default route.', 'statusCode': 200}