from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_aws.helpers.Rest_API import Rest_API

class test_Rest_API(Test_Helper):

    def setUp(self):
        self.name = 'temp-unit-test-api'
        super().setUp()
        self.rest_api = Rest_API(self.name)

    def test_add_method_http(self):
        from_path   =  '/'
        from_method = 'GET'
        to_method   = 'GET'
        to_uri      = 'http://httpbin.org/robots.txt'
        self.rest_api.add_method_http(from_path, from_method, to_method, to_uri)
        self.result = self.rest_api.test_method(from_path, from_method)

    def test_create(self):
        self.result = self.rest_api.create()

    def test_id(self):
        self.result = self.rest_api.id()

    def test_exists(self):
        self.result = self.rest_api.exists()

    #def test_resource(self):
    #

    def test_resource_id(self):
        self.result = self.rest_api.resource_id('/')

# this is the code that creates the lambda function used by the Shopify SendOWL Add on
class test_Rest_API__Create_Key_Generator(Test_Helper):

    def setUp(self):
        super().setUp()

    def test_setup_lambda_route(self):
        name        = 'api-key-generator-for-shopify'
        lambda_name = 'gw_bot_lambdas_gw_store_create_api_gw_api_key'
        rest_api    = Rest_API(name).create()
        rest_api.add_method_lambda('/','GET',lambda_name)
        rest_api.deploy()
        self.result = rest_api.test_method('/','GET')
        #self.result = rest_api.api_gateway.integration_add_permission_to_lambda(lambda_name)

    def test_just_invoke(self):
        name = 'api-key-generator-for-shopify'
        self.result = Rest_API(name).test_method().get('body')


