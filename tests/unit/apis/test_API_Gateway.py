from datetime import date, timedelta

from gw_bot.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.API_Gateway import API_Gateway


class test_API_Gateway(Test_Helper):

    def setUp(self):
        super().setUp()
        self.api_gateway        = API_Gateway()
        self.test_api_id        = 'xugc5ib648'  # VP-SaaS-Proxy
        self.test_resource_id   = 'lf80sgepa5'
        self.test_usage_plan_id = '7a6fl9'

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
        items = self.api_gateway.deployments(self.test_api_id)
        assert len(items) > 2

    def test_domain_names(self):
        assert len(self.api_gateway.domain_names()) > 0

    #not working: 'Invalid Method identifier specified'
    def test_integration(self):
       self.result = self.api_gateway.integration(self.test_api_id, self.test_resource_id, 'POST')

    #not working: 'Invalid Method identifier specified'
    def test_method(self):
       self.result = self.api_gateway.method(self.test_api_id, self.test_resource_id, 'POST')

    def test_models(self):
        assert len(self.api_gateway.models(self.test_api_id)) > 1

    def test_resources(self):
        assert len(self.api_gateway.resources(self.test_api_id)) > 1

    def test_rest_apis(self):
        items = self.api_gateway.rest_apis(index_by='id')
        assert self.test_api_id in items

    def test_stages(self):
        self.result = self.api_gateway.stages(self.test_api_id)

    def test_usage(self):
        days = 100
        self.result = self.api_gateway.usage(self.test_usage_plan_id, days)

    def test_usage_plans(self):
        assert self.api_gateway.usage_plans().get(self.test_usage_plan_id).get('name') == '1k month'