from datetime import date, timedelta

from osbot_aws.apis.Session import Session


class API_Gateway:

    def __init__(self):
        self.api_gateway = Session().client('apigateway')

    # helper methods

    # see this tweet to understand the use of the 'data_key' param https://twitter.com/DinisCruz/status/1226113182240038912
    # todo: add support for getting all the data using the position field
    def _call_method_return_items(self, method_name, params={}, index_by='id', data_key='items'):
        try:
            raw_data = getattr(self.api_gateway, method_name)(**params)
            data = {}
            print('-----')
            for item in raw_data.get(data_key):
                data[item.get(index_by)] = item
            return data
        except Exception as error:
            return {'error' : f'{error}'}

    def _call_method_return_arrays(self, method_name, params={}, index_by='id', data_key='items'):
        try:
            raw_data = getattr(self.api_gateway, method_name)(**params)
            data = {}

            for key,value in raw_data.get(data_key).items():
                data[key] = value
            return data
        except Exception as error:
            return {'error' : f'{error}'}

    def _get(self, target, params={}, index_by='id'):
        return self._call_method_return_items(method_name=f"get_{target}", params=params, index_by=index_by)

    def _get_using_api_id(self, target, api_id, index_by='id', data_key='items'):
        return self._call_method_return_items(method_name=f"get_{target}", params={'restApiId': api_id}, index_by=index_by, data_key=data_key)

    # main methods
    def account(self):
        return self.api_gateway.get_account()

    def api_keys(self, index_by='id'):
        return self._call_method_return_items(method_name="get_api_keys", index_by=index_by)

    def deployments(self, api_id):
        return self._call_method_return_items(method_name="get_deployments", params={'restApiId':api_id})

    def domain_names(self):
        return self.api_gateway.get_domain_names().get('items')

    def integration(self, api_id, resource_id, http_method):
       return self._call_method_return_items('get_integration', params={'restApiId': api_id, 'resourceId': resource_id, 'httpMethod': http_method})

    def method(self, api_id, resource_id, http_method):
        return self._call_method_return_items('get_method', params={'restApiId': api_id, 'resourceId': resource_id, 'httpMethod': http_method})

    def models(self, api_id):
        return self._get_using_api_id('models', api_id)

    def resources(self, api_id):
        return self._get_using_api_id('resources', api_id)

    def rest_apis(self, index_by='id'):
        return self._call_method_return_items(method_name="get_rest_apis",index_by=index_by)

    def stages(self, api_id):
        return self._get_using_api_id('stages', api_id, index_by='deploymentId', data_key='item')



    def usage_raw(self, usage_plan_id, days):
        start_date = (date.today() - timedelta(days=days)).strftime("%Y-%m-%d")
        end_date   = date.today().strftime("%Y-%m-%d")
        raw_data   = self._call_method_return_arrays(method_name= 'get_usage',params={'usagePlanId':usage_plan_id ,'startDate'  : start_date   , 'endDate'    : end_date})
        return raw_data




    def usage(self, usage_plan_id, days):
        if days > 90:
            days =90
        results = {}
        raw_data = self.usage_raw(usage_plan_id, days)
        for key, value in raw_data.items():
            key_results = {}
            for i in range(0,days):
                row_date = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
                key_results[row_date] = value[days-i][0]
            results[key] = key_results
        return results

    def usage_plans(self):
        return self._get('usage_plans')