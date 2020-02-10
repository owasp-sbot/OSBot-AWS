from datetime import date, timedelta
from time import sleep

from osbot_aws.apis.IAM import IAM

from osbot_aws.apis.Session import Session

from gw_bot.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.API_Gateway import API_Gateway
from osbot_aws.helpers.Rest_API import Rest_API


class test_API_Gateway(Test_Helper):

    def setUp(self):
        super().setUp()
        self.api_gateway        = API_Gateway()
        self.test_api_id        = 'xugc5ib648'  # VP-SaaS-Proxy
        self.test_api_key_id    = '24owcfrcjc'
        self.test_resource_id   = 'lf80sgepa5'
        self.test_usage_plan_id = '7a6fl9'


    def test__init__(self):
        assert type(self.api_gateway.api_gateway).__name__ == 'APIGateway'

    def test_account(self):
        #from osbot_jupyter.utils.Trace_Call import Trace_Call
        #trace = Trace_Call()
        #trace.include_filter=['osbot*', 'gwbot*','boto*','ConnectionPool*']
        #self.result = trace.invoke_method(self.api_gateway.account)

        account = self.api_gateway.account()
        assert account.get('apiKeyVersion')     == '4'
        assert account.get('cloudwatchRoleArn') == 'arn:aws:iam::311800962295:role/api-gateway-write-to-cloud-watch'
        assert account.get('features')          == ['UsagePlans']
        assert account.get('throttleSettings')  == {'burstLimit': 5000, 'rateLimit': 10000.0}

    def test_api_key(self):
        assert 'value' in set(self.api_gateway.api_key(self.test_api_key_id, include_value=True))

    def test_api_key_create__delete(self):
        key_name = 'temp new key'
        api_keys = self.api_gateway.api_keys()                      # store current api_keys
        api_key  = self.api_gateway.api_key_create(key_name)        # create key
        self.api_gateway.api_key_delete(key_id=api_key.get('id'))   # delete it using `id`
        self.api_gateway.api_key_create(key_name)                   # create it again
        self.api_gateway.api_key_delete(key_name=key_name)          # delete it using `name`
        assert api_keys == self.api_gateway.api_keys()              # confirm api_keys are unchanged

    def test_api_keys(self):
        keys = self.api_gateway.api_keys('name',include_values=True)
        assert len(keys) > 1
        assert list(keys.values()).pop().get('enabled') == True

    def test_deployments(self):
        items = self.api_gateway.deployments(self.test_api_id)
        assert len(items) > 2

    def test_domain_names(self):
        assert len(self.api_gateway.domain_names()) > 0

    #not working: 'Invalid Method identifier specified'
    def test_integration(self):
        api_name    = 'Slack GW-Bot'  #'Jira Sync' #'VP-SaaS-Proxy'
        path        = '/slack-handler' #'/jira-on-change' # '/{proxy+}'
        http_method = 'POST'
        api_id      = self.api_gateway.rest_api_id(api_name)
        resource_id = self.api_gateway.resource_id(api_id, path)
        self.result = self.api_gateway.integration(api_id, resource_id, http_method)

    def test_method_invoke_test(self):
        rest_api    = Rest_API('temp_rest_api').create()
        api_id      = rest_api.id()
        resource_id = rest_api.resource_id('/')
        method      = 'GET'
        self.result = self.api_gateway.method_invoke_test(api_id,resource_id,method)

    def test_integration_create__http(self):
        uri                = 'http://httpbin.org/robots.txt'
        rest_api           = Rest_API('temp_rest_api').delete().create()
        method             = 'GET'
        integration_method = 'GET'
        api_id             = rest_api.id()
        resource_id        = rest_api.resource_id('/')
        self.api_gateway.method_create(api_id, resource_id, method)
        self.result = self.api_gateway.integration_create__http(api_id=api_id, resource_id=resource_id, uri=uri, http_method=method, integration_http_method=integration_method)

    def test_integration_create__lambda(self):
        iam         = IAM()
        aws_region  = iam.region()
        aws_acct_id = iam.account_id()
        lambda_name = 'temp_lambda'
        rest_api    = Rest_API('temp_rest_api').create()
        api_id      = rest_api.id()
        resource_id = rest_api.resource_id('/')
        self.result = self.api_gateway.integration_create__lambda(api_id     =api_id     , resource_id=resource_id, aws_region=aws_region,
                                                                  aws_acct_id=aws_acct_id, lambda_name=lambda_name)

    def test_integration_response(self):
        rest_api    = Rest_API('temp_rest_api').create()
        api_id      = rest_api.id()
        resource_id = rest_api.resource_id('/')
        method      = 'POST'
        status_code = '200'
        self.result = self.api_gateway.integration_response(api_id, resource_id,method, status_code)

    def test_integration_response_create(self):
        rest_api           = Rest_API('temp_rest_api').create()
        api_id             = rest_api.id()
        resource_id        = rest_api.resource_id('/')
        method             = 'GET'
        status_code        = '200'
        response_templates = {'application/json': ''}
        self.result = self.api_gateway.integration_response_create(api_id, resource_id,method, status_code, response_templates)



    def test_method(self):
        api_name         = 'VP-SaaS-Proxy'
        path             = '/{proxy+}'
        api_id           = self.api_gateway.rest_api_id(api_name)
        resource_id      = self.api_gateway.resource_id(api_id, path)
        resource_method  = self.api_gateway.resource_methods(api_id, path).pop()
        method           = self.api_gateway.method(api_id, resource_id, resource_method)
        assert method.get('httpMethod') == resource_method

    def test_method_create__delete(self):
        api_name = 'temp-unit-test-api'
        path     = '/'
        method   = 'POST'
        api_id      = self.api_gateway.rest_api_create(api_name).get('id')                  # create api
        resource_id = self.api_gateway.resource(api_id, path).get('id')                     # get resource id
        self.result = self.api_gateway.method_create(api_id, resource_id,method)            # create method
        assert method in self.api_gateway.resource_methods(api_id, path)                    # confirm it exists
        self.result = self.api_gateway.method_delete(api_id, resource_id,method)            # delete method
        assert [] == self.api_gateway.resource_methods(api_id, path)                        # confirm it doesn't exist
        self.api_gateway.rest_api_delete(api_id)                                            # delete api

    def test_method_response(self):
        rest_api    = Rest_API('temp_rest_api').create()
        api_id      = rest_api.id()
        resource_id = rest_api.resource_id('/')
        method      = 'GET'
        status_code = '200'
        self.result = self.api_gateway.method_response(api_id, resource_id,method, status_code)

    def test_method_response_create(self):
        rest_api        = Rest_API('temp_rest_api').create()
        api_id          = rest_api.id()
        resource_id     = rest_api.resource_id('/')
        http_method     = 'GET'
        status_code     = '200'
        response_models = {'application/json': 'Empty'}
        self.result = self.api_gateway.method_response_create(api_id,resource_id,http_method,status_code,response_models)

        #self.result = self.api_gateway.method_invoke_test(api_id, resource_id, http_method)

    def test_models(self):
        assert len(self.api_gateway.models(self.test_api_id)) > 1

    def test_resource_create(self):
        api_name    = 'temp-unit-test-api'
        new_path    = 'test-path'

        # create Rest API
        rest_api    = self.api_gateway.rest_api_create(api_name)
        api_id      = rest_api.get('id')
        path_id     = self.api_gateway.resource(api_id, '/').get('id')

        # create resource
        new_path_id = self.api_gateway.resource_create(api_id,path_id,new_path).get('id')

        # confirm resource exists
        assert self.api_gateway.resource(api_id, f'/{new_path}').get('id') == new_path_id

        # delete resource and Rest API
        self.api_gateway.resource_delete(api_id, new_path_id)
        sleep(2)                                                # without this we get the botocore.errorfactory.TooManyRequestsException
        self.api_gateway.rest_api_delete(api_id)


    def test_resources(self):
        assert len(self.api_gateway.resources(self.test_api_id)) > 1
        assert self.api_gateway.resources('VP-SaaS-Proxy').get('id') == self.test_api_id
        assert self.api_gateway.resources('AAAA-BBB') == {'error': 'API not found: AAAA-BBB'}

    def test_rest_api_create__delete(self):
        rest_api = self.api_gateway.rest_api_create('temp test api ABC')            # create rest_api
        sleep(1)                                                                    # wait a little before deleting
        self.result = self.api_gateway.rest_api_delete(rest_api.get('id'))          # delete it
        try:
            pass
        except Exception as error:
            self.result = f'{error}'

    def test_rest_apis(self):
        items = self.api_gateway.rest_apis(index_by='id')
        assert self.test_api_id in items

    def test_stages(self):
        self.result = self.api_gateway.stages(self.test_api_id)

    def test_usage(self):
        days = 10
        usage = self.api_gateway.usage(self.test_usage_plan_id, days)
        assert len(usage) > 1
        assert len(usage[self.test_api_key_id]) == days

    def test_usage__as_chart_data(self):
        days = 10
        print('-----')
        self.result = self.api_gateway.usage__as_chart_data(self.test_usage_plan_id, days)

    def test_usage_plans(self):
        assert self.api_gateway.usage_plans().get(self.test_usage_plan_id).get('name') == '1k month'