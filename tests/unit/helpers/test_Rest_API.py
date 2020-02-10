from gw_bot.helpers.Test_Helper import Test_Helper
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