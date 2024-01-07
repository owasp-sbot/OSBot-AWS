from pprint import pprint


from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_aws.helpers.Rest_API import Rest_API

class test_Rest_API(Test_Helper):

    test_rest_api_name = 'temp-unit-test-api'

    @staticmethod
    def setup_test_enviroment__Rest_API(cls):            # todo: refactor into separate class
        rest_api = Rest_API(cls.test_rest_api_name)
        rest_api.create()

    @staticmethod
    def teardown_test_enviroment__Rest_API(cls):
        rest_api = Rest_API(cls.test_rest_api_name)
        assert rest_api.delete().not_exists()

    @classmethod
    def setUpClass(cls) -> None:
        cls.setup_test_enviroment__Rest_API(cls)

    @classmethod
    def tearDownClass(cls):
        cls.teardown_test_enviroment__Rest_API(cls)

    def setUp(self):
        super().setUp()
        self.rest_api = Rest_API(self.test_rest_api_name)

    def test__init__(self):
        assert self.rest_api.api_name == self.test_rest_api_name
        assert self.rest_api.api_id   is None

    def test_add_method_http(self):
        from_path   =  '/'
        from_method = 'GET'
        to_method   = 'GET'
        to_uri      = 'http://httpbin.org/robots.txt'
        self.rest_api.add_method_http(from_path, from_method, to_method, to_uri)
        assert len(self.rest_api.test_method(from_path, from_method).get('log')) > 0

    def test_create(self):
        current_id = self.rest_api.id()
        self.rest_api.create()                        # note: calling create on a method that already exists will not do anything
        assert self.rest_api.api_id == current_id     # confirm value is set

    def test_id(self):
        assert self.rest_api.id() == self.rest_api.api_id

    def test_exists(self):
        assert self.rest_api.exists() is True

    #def test_resource(self):
    #

    def test_resource_id(self):
        self.rest_api.resource_id('/') == self.rest_api.api_id



# # this is the code that creates the lambda function used by the Shopify SendOWL Add on
# class test_Rest_API__Create_Key_Generator(Test_Helper):
#
#     def setUp(self):
#         super().setUp()
#
#     def test_setup_lambda_route(self):
#         name        = 'api-key-generator-for-shopify'
#         lambda_name = 'gw_bot_lambdas_gw_store_create_api_gw_api_key'
#         rest_api    = Rest_API(name).create()
#         rest_api.add_method_lambda('/','GET',lambda_name)
#         rest_api.deploy()
#         self.result = rest_api.test_method('/','GET')
#         #self.result = rest_api.api_gateway.integration_add_permission_to_lambda(lambda_name)
#
#     def test_just_invoke(self):
#         name = 'api-key-generator-for-shopify'
#         self.result = Rest_API(name).test_method().get('body')


