# NOT WORKING (TO TRY Later)
import json

import botocore
import requests
from botocore.httpsession import URLLib3Session

from osbot_aws.apis.Lambda import Lambda
from osbot_aws.apis.test_helpers.Temp_Lambda import Temp_Lambda

from gw_bot.helpers.Test_Helper import Test_Helper
#from osbot_aws.apis.Lambda_Http import Lambda_Http
from osbot_aws.helpers.Method_Wrappers import aws_inject
from osbot_utils.decorators.trace import trace


class test_Lambda_Http(Test_Helper):

    #@aws_inject('region,account_id')
    def setUp(self):#, region, account_id):
        super().setUp()
        self.lambda_name  = 'temp_lambda_HL58KB'
 #       self.lambda_http = Lambda_Http(self.lambda_name)

    def test_create_temp_lambda(self):
        with Temp_Lambda() as temp_lambda:
            temp_lambda.delete_on_exit = False
            self.result = temp_lambda.lambda_name     # temp_lambda_LVY1LL

    #@trace
    def test_find_the_key(self):
        aws_lambda = Lambda(self.lambda_name)
        self.result = aws_lambda.invoke({'name': '123'})
        #self.result = aws_lambda.functions(index_by='FunctionName').keys().type()

    #def test_make_request(self):
    #    self.result = self.lambda_http.make_request()

    def test_recreate_request(self):

        client = Lambda().client()
        operation_model = client._service_model.operation_model('Invoke')
        self.result = operation_model

        payload = {"name": "bbbbaaaa"}
        request_dict= {'url_path': '/2015-03-31/functions/temp_lambda_HL58KB/invocations',
                       'query_string': {},
                       'method': 'POST',
                       'headers': {},
                       'body': json.dumps(payload)}
        endpoint_url = 'https://lambda.eu-west-1.amazonaws.com'
        user_agent='Boto3/1.12.5 Python/3.8.1 Darwin/18.7.0 Botocore/1.15.5'

        from botocore.awsrequest import prepare_request_dict

        prepare_request_dict(request_dict=request_dict,endpoint_url=endpoint_url,user_agent=user_agent)
        request = client._endpoint.create_request(request_dict, operation_model)

        headers = {'User-Agent': b'Boto3/1.12.5 Python/3.8.1 Darwin/18.7.0 Botocore/1.15.5', 'X-Amz-Date': b'20200224T010440Z', 'Authorization': b'AWS4-HMAC-SHA256 Credential=AKIAURGGJDT3TXD5DCXK/20200224/eu-west-1/lambda/aws4_request, SignedHeaders=host;x-amz-date, Signature=3ea5c19cc097466202e71c4e3b4e306327709442138bfd6443b27a25cfd89c91', 'Content-Length': '15'}
        self.result = requests.post(request.url,json=payload,headers=request.headers).text
        #self.result = request.url
        #http_session = URLLib3Session()

        #self.result = http_session.send(request).text
        #self.result = request.headers.items()
        return
        from botocore.endpoint import Endpoint
        endpoint = Endpoint()
        self.params = { 'url_path': '/2015-03-31/functions/temp_lambda_HL58KB/invocations', 'query_string': {},
                        'method'  : 'POST',
                        'headers' : {'User-Agent': 'Boto3/1.12.5 Python/3.8.1 Darwin/18.7.0 Botocore/1.15.5'},
                        'body'    : b'{"name": "123"}',
                        'url'     : 'https://lambda.eu-west-1.amazonaws.com/2015-03-31/functions/temp_lambda_HL58KB/invocations',
                        'context' : {'client_region': 'eu-west-1',
                                    'client_config': None, 'has_streaming_input': True, 'auth_type': None}}
        #< botocore.config.Config object at0x10f5802e0 >
        self.result =42