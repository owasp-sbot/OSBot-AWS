from datetime import date, timedelta

from osbot_aws.apis.Session import Session


class API_Gateway:

    def __init__(self):
        self.api_gateway = Session().client('apigateway')

    # helper methods
    def _call_method(self, method_name, params):
        try:
            return getattr(self.api_gateway, method_name)(**params)
        except Exception as error:
            return {'error': f'{error}'}
    # see this tweet to understand the use of the 'data_key' param https://twitter.com/DinisCruz/status/1226113182240038912
    # see this tweet thread to see more info about performance issues with this api https://twitter.com/DinisCruz/status/1226504297439023104
    # todo: add support for getting all the data using the position field
    def _call_method_return_items(self, method_name, params={}, index_by='id', data_key='items'):
        try:
            raw_data = getattr(self.api_gateway, method_name)(**params)
            data = {}
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

    def api_keys(self, index_by='id',include_values=False):
        return self._call_method_return_items(method_name="get_api_keys", params={'includeValues':include_values}, index_by=index_by)

    def api_key(self, api_key, include_value=False):
        return self.api_gateway.get_api_key(apiKey=api_key,includeValue=include_value)

    def api_key_create(self,key_name):
        return self.api_gateway.create_api_key(name=key_name)

    def api_key_delete(self, key_id=None, key_name=None):
        if key_id:
            return self.api_gateway.delete_api_key(apiKey=key_id)
        if key_name:
            for key_id, value in self.api_keys().items():
                if value.get('name') == key_name:
                    return self.api_gateway.delete_api_key(apiKey=key_id)

    def deployments(self, api_id):
        return self._call_method_return_items(method_name="get_deployments", params={'restApiId':api_id})

    def domain_names(self):
        return self.api_gateway.get_domain_names().get('items')

    def integration(self, api_id, resource_id, http_method):
        return self.api_gateway.get_integration(restApiId=api_id, resourceId=resource_id, httpMethod=http_method)

    def integration_create__http(self, api_id, resource_id, uri, http_method='GET', integration_http_method='GET'):
        input_type        = 'HTTP'
        # methodIntegration = {'httpMethod' : 'GET' }
        try:
        #     return self.api_gateway.put_integration(
        #         restApiId             = 'dw51p7dutg',
        #         resourceId            = '4k04b51pm9',
        #         httpMethod            = "POST",
        #         type                  = "HTTP",
        #         integrationHttpMethod = "POST",
        #         uri                   = "http://httpbin.org/robots.txt",
        #         connectionType        = 'INTERNET',
        #         requestParameters     = {},
        #         passthroughBehavior   = 'WHEN_NO_MATCH' ,
        #         cacheNamespace        = '4k04b51pm9')

            return self.api_gateway.put_integration(restApiId=api_id,
                                                    resourceId=resource_id,
                                                    httpMethod=http_method,
                                                    integrationHttpMethod=integration_http_method,
                                                    type=input_type,
                                                    uri=uri)
        except Exception as error:
            return f'{error}'

    def integration_create__lambda(self, api_id, resource_id, aws_region, aws_acct_id, lambda_name, http_method='POST'):
        input_type = 'AWS'
        uri = f'arn:aws:apigateway:{aws_region}:lambda:path/2015-03-31/functions/arn:aws:lambda:{aws_region}:{aws_acct_id}:function:{lambda_name}/invocations'
        try:
            return self.api_gateway.put_integration(restApiId=api_id, resourceId=resource_id, httpMethod=http_method,
                                                    integrationHttpMethod=http_method,type=input_type, uri=uri)
        except Exception as error:
            return f'{error}'

    def integration_response(self, api_id, resource_id, http_method, status_code):
        params = {'restApiId': api_id,
                  'resourceId': resource_id,
                  'httpMethod': http_method,
                  'statusCode': status_code,
                  }
        return self._call_method('get_integration_response', params)

    def integration_response_create(self, api_id, resource_id, http_method, status_code,response_templates):
        params = {'restApiId'        : api_id,
                  'resourceId'       : resource_id,
                  'httpMethod'       : http_method,
                  'statusCode'       : status_code,
                  'responseTemplates': response_templates
                  }
        return self._call_method('put_integration_response', params)

    def method(self, api_id, resource_id, http_method):
        try:
            return self.api_gateway.get_method(restApiId=api_id, resourceId= resource_id, httpMethod= http_method)
        except Exception as error:
            return {'error': f'{error}'}

    def method_create(self, api_id, resource_id, http_method, authorization_type='NONE'):
        return self._call_method("put_method", { 'restApiId': api_id, 'resourceId':resource_id, 'httpMethod':http_method, 'authorizationType':authorization_type})
#        return self.api_gateway.put_method(restApiId=api_id, resourceId=resource_id, httpMethod=http_method, authorizationType=authorization_type)

    def method_delete(self, api_id, resource_id, http_method):
        return self.api_gateway.delete_method(restApiId=api_id, resourceId=resource_id, httpMethod=http_method)

    def method_invoke_test(self, api_id,resource_id,http_method, path_with_query_string='',body='',headers={}):
        params = { 'restApiId'          : api_id ,
                   'resourceId'         : resource_id,
                   'httpMethod'         : http_method,
                   'pathWithQueryString': path_with_query_string,
                   'body'               : body   ,
                   'headers'            : headers}
        return self._call_method("test_invoke_method", params)

    def method_response(self,api_id,resource_id,http_method,status_code):
        params = { 'restApiId' : api_id ,
                   'resourceId': resource_id,
                   'httpMethod': http_method,
                   'statusCode': status_code,
                   }
        return self._call_method('get_method_response', params)

    def method_response_create(self,api_id,resource_id,http_method,status_code,response_models):
        params = { 'restApiId'     : api_id ,
                   'resourceId'    : resource_id ,
                   'httpMethod'    : http_method ,
                   'statusCode'    : status_code ,
                   'responseModels': response_models
                   }
        return self._call_method('put_method_response', params)

    def models(self, api_id):
        return self._get_using_api_id('models', api_id)

    def resource(self, api_id, path):
        return self.resources(api_id, index_by='path').get(path,{})

    def resource_id(self, api_id, path):
        return self.resource(api_id,path).get('id')

    def resource_methods(self, api_id, path):
        return list(set(self.resource(api_id,path).get('resourceMethods',[])))

    def resource_create(self, api_id, parent_id, path):
        return self.api_gateway.create_resource(restApiId=api_id, parentId=parent_id,pathPart=path)

    def resource_delete(self, api_id, resource_id):
        return self.api_gateway.delete_resource(restApiId=api_id, resourceId=resource_id)

    def resources(self, api_id_or_name, index_by='id'):
        result = self._get_using_api_id('resources', api_id=api_id_or_name, index_by=index_by)
        if result.get('error') is None:
            return result
        rest_apis = self.rest_apis(index_by='name')
        if api_id_or_name in rest_apis:
            api_id = rest_apis.get(api_id_or_name).get('id')
            return self._get_using_api_id('resources', api_id=api_id, index_by=index_by)
        return {'error': f'API not found: {api_id_or_name}'}

    def rest_api(self, api_name):
        return self.rest_apis(index_by='name').get(api_name,{})

    def rest_api_create(self, api_name):
        rest_apis = self.rest_apis(index_by='name')                   # get existing Rest APIs
        if api_name in rest_apis:                                     # see if it already exists
            return rest_apis.get(api_name)                            # return if it does
        params = { 'name'                 : api_name               ,
                   'endpointConfiguration': {"types": ["REGIONAL"]}}
        return self.api_gateway.create_rest_api(**params)              # if not, create it

    def rest_api_delete(self, api_id):
        if self.rest_api_exists(api_id):
            self.api_gateway.delete_rest_api(restApiId=api_id)

    def rest_api_exists(self, api_id):
        return self.rest_api_info(api_id).get('id') == api_id

    def rest_api_id(self, api_name):
        return self.rest_api(api_name).get('id')

    def rest_api_info(self, api_id):
        try:
            return self.api_gateway.get_rest_api(restApiId=api_id)
        except Exception as error:
            return {'error': f'{error}'}

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

    # this method helps to create a table that is usable by graph engines like Google Charts
    def usage__as_chart_data(self,usage_plan_id, days):
        api_keys = self.api_keys()

        usage = self.usage(usage_plan_id, days)
        headers = ['Days','Totals']
        keys = sorted(list(set(usage)))
        for key in keys:
            name = api_keys[key].get('name')
            headers.append(name)
        rows = [headers]

        if len(keys) > 0:
            days = usage[keys[0]].keys()
            for day in days:
                row_key = day.replace('2020-','')
                row = [row_key]
                total = 0
                for key in keys:
                    value = usage[key][day]
                    row.append(value)
                    total += value
                row.insert(1,total)
                rows.insert(1,row)
                
        return rows

    def usage_plans(self):
        return self._get('usage_plans')



  # 'apiKeyRequired': False,
  # 'authorizationType': 'NONE',
  # 'httpMethod': 'GET',
  # 'methodIntegration': { 'cacheKeyParameters': [],
  #                        'cacheNamespace': '4k04b51pm9',
  #                        'connectionType': 'INTERNET',
  #                        'httpMethod': 'GET',
  #                        'integrationResponses': { '200': { 'responseTemplates': { 'application/json': None},
  #                                                           'statusCode': '200'}},
  #                        'passthroughBehavior': 'WHEN_NO_MATCH',
  #                        'timeoutInMillis': 29000,
  #                        'type': 'HTTP',
  #                        'uri': 'https://www.google.com'},
  # 'methodResponses': { '200': { 'responseModels': {'application/json': 'Empty'},
  #                               'statusCode': '200'}},
  # 'requestParameters': {}}
