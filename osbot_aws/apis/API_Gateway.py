from osbot_aws.apis.Session import Session


class API_Gateway:

    def __init__(self):
        self.api_gateway = Session().client('apigateway')

    def _call_method_return_items(self, method_name, params={}, index_by='id'):
        raw_data = getattr(self.api_gateway, method_name)(**params)
        data = {}
        for item in raw_data.get('items'):
            data[item.get(index_by)] = item
        return data

    def account(self):
        return self.api_gateway.get_account()

    def api_keys(self, index_by='id'):
        return self._call_method_return_items(method_name="get_api_keys", index_by=index_by)

    def deployments(self, api_key):
        return self._call_method_return_items(method_name="get_deployments", params={'restApiId':api_key})

    def domain_names(self):
        return self.api_gateway.get_domain_names().get('items')

    def rest_apis(self, index_by='id'):
        return self._call_method_return_items(method_name="get_rest_apis",index_by=index_by)