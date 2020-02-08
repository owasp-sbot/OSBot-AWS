from gw_bot.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.API_Gateway import API_Gateway


class test_API_Gateway(Test_Helper):

    def setUp(self):
        super().setUp()
        self.api_gateway  = API_Gateway()
        self.test_api_id = 'xugc5ib648'  # VP-SaaS-Proxy

    def test__init__(self):
        assert type(self.api_gateway.api_gateway).__name__ == 'APIGateway'

    def test_account(self):
        account = self.api_gateway.account()
        assert account.get('apiKeyVersion')     == '4'
        assert account.get('cloudwatchRoleArn') == 'arn:aws:iam::311800962295:role/api-gateway-write-to-cloud-watch'
        assert account.get('features')          == ['UsagePlans']
        assert account.get('throttleSettings')  == {'burstLimit': 5000, 'rateLimit': 10000.0}

    def test_api_keys(self):
        keys = self.api_gateway.api_keys('name')
        assert len(keys) > 1
        assert list(keys.values()).pop().get('enabled') == True

    def test_deployments(self):
        self.result = self.api_gateway.deployments(self.test_api_id)

    def test_domain_names(self):
        assert self.api_gateway.domain_names() == []

    def test_rest_apis(self):
        items = self.api_gateway.rest_apis(index_by='id')
        assert self.test_api_id in items

        #self.result = self.api_gateway._call_method_return_items('get_rest_apis')#, {'restApiId': self.test_api_id})