import os
from unittest                                                   import TestCase

import pytest

from osbot_aws.AWS_Config                                        import AWS_Config
from osbot_aws.aws.apigateway.apigw_dydb.WS__DyDB                import WS__DyDB
from osbot_aws.aws.apigateway.lambdas.Deploy__lambda_web_sockets import Deploy__lambda_web_sockets
from osbot_aws.aws.apigateway.lambdas.lambda_web_sockets         import run
from osbot_aws.testing.TestCase__Lambda                          import TestCase__Lambda
from osbot_aws.utils.Version                                     import version
from osbot_utils.utils.Misc                                      import random_guid

@pytest.mark.skip("need refactoring to deploy code - only need in test")
class test_lambda_web_sockets(TestCase__Lambda):

    def setUp(self):
        self.handler          = run
        self.aws_config       = AWS_Config()
        self.account_id       = self.aws_config.account_id()
        self.region_name      = self.aws_config.region_name()
        self.aws_lambda       = self.type_Lambda(name=self.handler.__module__)
        self.function_name    = self.aws_lambda.name
        self.role_name        = 'temp_role_for_lambda_invocation'
        self.runtime_hash     = '1bebe65bb4f19dd8c37baeb0be18a0b278155b42bfe12dd28480199436d18229'
        self.version          = version
        self.dydb_ws          = WS__DyDB(dynamo_db=self.dynamo_db)
        #self.api_gw_id        = os.environ.get('API_GW__WEB_SOCKETS')                                      # todo wire up websocket workflow
        #self.wss_host         = f'{self.api_gw_id}.execute-api.{self.region_name}.amazonaws.com'
        #self.wss_endpoint     = f'wss://{self.wss_host}'
        #self.wss_endpoint_uri = f'{self.wss_endpoint}/prod/'


    # def tearDown(self):
    #     assert self.dydb_ws.size() == 0

    def deploy_lambda(self):
        deploy = Deploy__lambda_web_sockets()
        update_result = deploy.update()
        assert update_result == 'Successful'
        return deploy

    @pytest.mark.skip('Only used locally when needing to make regular changes to the lambda function')
    def test___deploy_lambda(self):
        # if True: #Web_Utils.in_aws_code_build():
        #     pytest.skip('Only used locally when needing to make regular changes to the lambda function')
        deploy = self.deploy_lambda()
        invoke_result = deploy.invoke_lambda()
        assert invoke_result == {'statusCode': 400, 'body': 'Route not recognized.'}

    def test__aws_lambda_config(self):
        with self.aws_lambda as _:
            configuration = _.configuration()

            assert _.name       == 'osbot_aws_aws_apigateway_lambdas_lambda_web_sockets'
            assert _.name       == self.function_name
            assert _.exists()   is True
            assert configuration == { 'Architectures'       : ['x86_64']                                                                               ,
                                      'CodeSha256'          : configuration.get('CodeSha256')                                                          ,
                                      'CodeSize'            : configuration.get('CodeSize')                                                            ,
                                      'Description'         : ''                                                                                       ,
                                      'EphemeralStorage'    : {'Size': 512}                                                                            ,
                                      'FunctionArn'         : f'arn:aws:lambda:{self.region_name}:{self.account_id}:function:{self.function_name}'     ,
                                      'FunctionName'        : self.function_name                                                                       ,
                                      'Handler'             : f'{self.handler.__module__}.run'                                                         ,
                                      'LastModified'        : configuration.get('LastModified')                                                        ,
                                      'LastUpdateStatus'    : 'Successful'                                                                             ,
                                      'LoggingConfig'       : { 'LogFormat': 'Text', 'LogGroup' : f'/aws/lambda/{self.function_name}'                 },
                                      'MemorySize'          : 512                                                                                      ,
                                      'PackageType'         : 'Zip'                                                                                    ,
                                      'RevisionId'          : configuration.get('RevisionId')                                                          ,
                                      'Role'                : f'arn:aws:iam::{self.account_id}:role/{self.role_name}'                                  ,
                                      'Runtime'             : 'python3.11'                                                                             ,
                                      'RuntimeVersionConfig': { 'RuntimeVersionArn': f'arn:aws:lambda:{self.region_name}::runtime:{self.runtime_hash}'},
                                      'SnapStart'           : {'ApplyOn': 'None', 'OptimizationStatus': 'Off'                                         },
                                      'State'               : 'Active'                                                                                 ,
                                      'Timeout'             : 60                                                                                       ,
                                      'TracingConfig'       : {'Mode': 'PassThrough'                                                                  },
                                      'Version'             : '$LATEST'                                                                                }

    def test__lambda_invoke__connect(self):

        payload = {}
        assert self.aws_lambda.invoke(payload) == {'body': 'Route not recognized.', 'statusCode': 400}
        connection_id = random_guid()
        payload = {'requestContext': { 'connectionId': connection_id,
                                       'routeKey'    : '$connect' }}

        assert self.aws_lambda.invoke(payload) == { 'body'         : 'Connected.' ,
                                                    'statusCode'   : 200          }

        payload = {'requestContext': { 'connectionId': connection_id,
                                       'routeKey'    : '$disconnect' }}
        assert self.aws_lambda.invoke(payload) == { 'body'         : 'Disconnected.' ,
                                                    'statusCode'   : 200          }

        document = self.dydb_ws.document(connection_id)
        event_1  =document.get('events')[0]
        event_2  =document.get('events')[1]
        assert { 'date': document.get('date'),
                  'env': 'LOCAL',
                  'events': [ { 'action': 'connect',
                                'lambda_event': { 'requestContext': { 'connectionId': connection_id,
                                                                      'routeKey': '$connect'}},
                                'source': '',
                                'status': 'active',
                                'timestamp': event_1.get('timestamp')},
                              { 'action': 'disconnect',
                                'lambda_event': { 'requestContext': { 'connectionId': connection_id,
                                                                      'routeKey': '$disconnect'}},
                                'source': '',
                                'status': 'disconnected',
                                'timestamp': event_2.get('timestamp')}],
                  'id': connection_id,
                  'status': 'disconnected',
                  'timestamp': event_1.get('timestamp'),
                  'timestamp_disconnect': event_2.get('timestamp'),
                  'version': 'v0.76.26'}
        self.dydb_ws.delete_document(connection_id)

    # todo: wire up this test
    # def test__api_gateway_config(self):
    #     api_gateway    = API_Gateway_V2()
    #     api_gw_details = api_gateway.api(self.api_gw_id)
    #     assert api_gw_details == { 'ApiEndpoint'                : self.wss_endpoint                                                     ,
    #                                'ApiId'                      : self.api_gw_id                                                        ,
    #                                'ApiKeySelectionExpression'  : '$request.header.x-api-key'                                           ,
    #                                'CreatedDate'                : api_gw_details.get('CreatedDate')                                     ,
    #                                'DisableExecuteApiEndpoint'  : False                                                                 ,
    #                                'Name'                       : self.api_gw_name                                                      ,
    #                                'ProtocolType'               : 'WEBSOCKET'                                                           ,
    #                                'RouteSelectionExpression'   : '$request.body.action'                                                ,
    #                                'Tags'                       : {}                                                                    }

    # todo: wire up this test
    # def test__websocket__connect(self):
    #     if Web_Utils.in_aws_code_build():
    #         pytest.skip('Skipping test since it not working reliably on AWS Code Build')
    #
    #     #self.deploy_lambda()
    #     import asyncio
    #     import websockets
    #     async def connect(uri):
    #         async with websockets.connect(uri) as websocket:
    #             assert websocket.closed is False
    #             assert websocket.host   == self.wss_host         # todo: see if there is another way to get this value since the alternatives methods described in the code don't provide this host information
    #             assert websocket.open   is True
    #             assert websocket.port   == 443
    #             assert websocket.secure is True
    #             assert websocket.side   == 'client'
    #
    #             await websocket.send('ping')                    # todo: add feature to dydb_ws to capture the incomming messages and the respective responses
    #
    #             response_raw              = await websocket.recv()
    #             response                  = from_json_str(response_raw)
    #             connection_id             = response.get('data').get('connection_id')
    #             dydb_document             = self.dydb_ws.dydb_document(connection_id)
    #             assert list_set(response)            == ['data', 'topic', 'when']
    #             assert dydb_document.value('status') == 'active'
    #
    #
    #         assert websocket.closed is True                     # confirm websocket is closed
    #         assert websocket.open   is False
    #         for i in range(0, 10):                               # wait for API GW event to fire and change the DyDB record
    #             if dydb_document.field('status') == 'disconnected':
    #                 break
    #             print(i, 'still active')
    #         assert dydb_document.value('status') == 'disconnected'
    #         assert len(dydb_document.value('events')) == 2
    #         dydb_document.delete()
    #
    #     asyncio.get_event_loop().run_until_complete(connect(self.wss_endpoint_uri))

    # todo: wire up this test
    # def test__websocket__send_and_receive_message(self):
    #     import asyncio
    #     import websockets
    #     async def connect(uri):
    #         async with websockets.connect(uri) as websocket:
    #             an_message = 'this is an message'
    #             await websocket.send(an_message)
    #             response      = from_json_str(await websocket.recv())
    #             assert list_set(response) == ['data', 'topic', 'when']
    #             connection_id = response.get('connection_id')
    #
    #         self.dydb_ws.delete_document(connection_id)
    #             #assert response == f'{{"message": "CCCCC Hi: ", "event": "on DEFAULT", "body": "{an_message}"}}'
    #
    #
    #     asyncio.get_event_loop().run_until_complete(connect(self.wss_endpoint_uri))

    # todo: wire up this test
    # def test_using_websockets(self):
    #     #self.deploy.update()
    #
    #     import asyncio
    #     import websockets
    #     import json
    #
    #     api_gw_id   = os.environ.get('API_GW__WEB_SOCKETS')
    #     async def send_message(uri, message):
    #         print('about to connect')
    #         async with websockets.connect(uri) as websocket:
    #             print('connected, about to send')
    #             await websocket.send(json.dumps(message))
    #             print('after send')
    #
    #             # Wait for server to response
    #             # If your server sends back a response, you can receive it here.
    #             response = await websocket.recv()
    #             print("Received:", response)
    #
    #     # Replace with your actual WebSocket server URI
    #     uri = 'wss://{api_gw_id}}.execute-api.eu-west-2.amazonaws.com/prod/'
    #     message = {'action': 'yourAction', 'data': 'AAABB'}
    #
    #     # Send a message to the server
    #     asyncio.get_event_loop().run_until_complete(send_message(uri, message))