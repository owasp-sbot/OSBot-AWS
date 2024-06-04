import pytest

from osbot_aws.aws.apigateway.apigw_dydb.WS__Handle_Events  import WS__Handle_Events
from osbot_aws.testing.TestCase__Dynamo_DB                  import TestCase__Dynamo_DB
from osbot_aws.utils.Version                                import version
from osbot_utils.utils.Json                                 import from_json_str
from osbot_utils.utils.Misc                                 import random_guid, list_set


@pytest.mark.skip("Needs AWS environment setup , in this case the Lambda function invoked below")
class test_WS__Handle_Events(TestCase__Dynamo_DB):
    connection_id   : str
    source          : str                = 'PyTest'
    ws_handle_event : WS__Handle_Events
    #version         : str

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ws_handle_event = WS__Handle_Events(source=cls.source)
        cls.ws_handle_event.dydb_ws.dynamo_db = cls.dynamo_db
        cls.connection_id = random_guid()


    @classmethod
    def tearDownClass(cls):
        #pprint(f'deleting connection_id: {cls.connection_id}')
        cls.ws_handle_event.dydb_ws.delete_document(cls.connection_id)



    def test__setup(self):
        with self.ws_handle_event as _:
            expected_vars = dict(dydb_ws = _.dydb_ws   ,
                                 source  = self.source,)
            assert _.__locals__() == expected_vars

    #@print_boto3_calls()
    def test_handle_lambda(self):

        with self.ws_handle_event as _:

            # unknown route
            result_route_route = self.invoke_route('unknown_route')
            assert result_route_route     == {'body': 'Route not recognized.', 'statusCode': 400}

            # $connect route
            result_route_route = self.invoke_route('$connect')
            assert result_route_route     == {'body': 'Connected.', 'statusCode': 200}

            # $disconnect route
            result_route_route = self.invoke_route('$disconnect')
            assert result_route_route     == {'body': 'Disconnected.', 'statusCode': 200}

            # $default route
            result_route_route = self.invoke_route('$default')
            result_body  = from_json_str(result_route_route.get('body'))
            status_code = result_route_route.get('statusCode')
            assert status_code                      == 200
            assert list_set(result_body)            == ['data', 'topic', 'when']

            self.check_data_in_dynamo_db__after_a_connect_disconnect_loop(self.connection_id)

    # helper test methods
    def check_data_in_dynamo_db__after_a_connect_disconnect_loop(self, connection_id):
        document      = self.ws_handle_event.dydb_ws.document(connection_id)
        document_date = document.get('date')
        document_env  = document.get('env')
        events        = document.get('events')
        event_1       = events[0]
        event_2       = events[1]

        assert document == { 'date'                 : document_date,
                             'env'                  : document_env,
                             'events'               : [ { 'action'       : 'connect'                                          ,
                                                           'lambda_event': { 'requestContext': { 'connectionId': connection_id,
                                                                                                 'routeKey'    : '$connect' }},
                                                           'source'      : self.source               ,
                                                           'status'      : 'active'                  ,
                                                           'timestamp'   : event_1.get('timestamp')} ,
                                                         { 'action'      : 'disconnect'              ,
                                                           'lambda_event': { 'requestContext': { 'connectionId': connection_id,
                                                                                                 'routeKey': '$disconnect'  }},
                                                           'source'      : self.source               ,
                                                           'status'      : 'disconnected'            ,
                                                           'timestamp'   : event_2.get('timestamp')}],
                              'id'                  : connection_id                                  ,
                              'status'              : 'disconnected'                                 ,
                              'timestamp'           : document.get('timestamp')                      ,
                              'timestamp_disconnect': event_2.get('timestamp' )                      ,
                              'version'             : version                                        }

    def invoke_route(self, route_key):
        context         = None
        request_content = {'connectionId': self.connection_id, 'routeKey': route_key}
        event           = {'requestContext': request_content}
        result          = self.ws_handle_event.handle_lambda(event, context)
        return result

    def test_route_default(self):
        #with self.ws_handle_event as _:
        with self.ws_handle_event.dydb_ws.dydb_document(self.connection_id) as _:
            result_route_route = self.invoke_route('$default')
            result_body        = from_json_str(result_route_route.get('body'))
            result_body_when   = result_body.get('when')
            assert result_route_route.get('statusCode') == 200
            assert result_body == { 'data': { 'action'       : 'show_message',
                                              'connection_id': self.connection_id           ,
                                              'response'     : {'message': "no command provided : {'request': None}"}},
                                    'topic'  : 'ws__dydb'       ,
                                    'when'   : result_body_when }


