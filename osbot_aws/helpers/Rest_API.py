from osbot_aws.apis.API_Gateway import API_Gateway


class Rest_API:
    def __init__(self, api_name=None, api_id=None):
        self.api_name    = api_name
        self.api_id      = api_id
        self.api_gateway = API_Gateway()

    def create(self):
        self.api_gateway.rest_api_create(self.api_name)
        return self

    def delete(self):
        self.api_gateway.rest_api_delete(self.id())
        self.api_id = None
        return self

    def id(self):
        if self.api_id is None:
            self.api_id = self.api_gateway.rest_api_id(self.api_name)
        return self.api_id

    def exists(self):
        return self.id() is not None

    def add_method_http(self, from_path, from_method, to_method, to_uri):
        resource_id     = self.resource_id(from_path)
        status_code     = '200'
        response_models = {'application/json': 'Empty'}
        response_templates = {'application/json': ''}
        method_create               = self.api_gateway.method_create(self.api_id, resource_id,from_method)
        integration_create__http    = self.api_gateway.integration_create__http(self.id(), resource_id,to_uri,from_method, to_method)
        method_response_create      = self.api_gateway.method_response_create(self.id(),resource_id,from_method, status_code,response_models)
        integration_response_create = self.api_gateway.integration_response_create(self.id(),resource_id, from_method,status_code, response_templates)
        return { 'method_create'              : method_create               ,
                 'integration_create__http'   : integration_create__http    ,
                 'method_response_create'     : method_response_create      ,
                 'integration_response_create': integration_response_create }

    def method(self, path, method):
        resource_id = self.resource_id(path)
        return self.api_gateway.method(self.id(), resource_id, method)

    def resource_id(self, path):
        return self.api_gateway.resource(self.id(), path).get('id')

    def test_method(self, path,method):
        return self.api_gateway.method_invoke_test(self.api_id,self.resource_id(path), method)