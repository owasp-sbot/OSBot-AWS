from datetime import date, timedelta

from osbot_aws.aws.iam.IAM import IAM
from osbot_utils.decorators.methods.cache_on_self import cache_on_self

from osbot_aws.aws.lambda_.Lambda import Lambda
from osbot_aws.apis.Session import Session


class API_Gateway:

    def __init__(self):
        pass

    @cache_on_self
    def api_gateway(self):
        return Session().client('apigateway')

    # helper methods
    def _call_method(self, method_name, params):
        try:
            return getattr(self.api_gateway(), method_name)(**params)
        except Exception as error:
            return {'error': f'{error}'}

    # see this tweet to understand the use of the 'data_key' param https://twitter.com/DinisCruz/status/1226113182240038912
    # see this tweet thread to see more info about performance issues with this api https://twitter.com/DinisCruz/status/1226504297439023104
    # todo: add support for getting all the data using the position field
    def _call_method_return_items(self, method_name, params={}, index_by='id', data_key='items'):
        try:
            raw_data = getattr(self.api_gateway(), method_name)(**params)
            data = {}
            for item in raw_data.get(data_key):
                data[item.get(index_by)] = item
            return data
        except Exception as error:
            return {'error' : f'{error}'}

    def _call_method_return_arrays(self, method_name, params={}, index_by='id', data_key='items'):
        try:
            raw_data = getattr(self.api_gateway(), method_name)(**params)
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

    def _index_by(self, values, index_by=None):
        if index_by is None:
            return list(values)
        results = {}
        for item in values:
            results[item.get(index_by)] = item
        return results

    # main methods
    def account(self):
        return self.api_gateway().get_account()

    #@aws_retry()  #todo add the code below to the aws_retry method (this is needed by operations that are affected by delays in IAM deployments
    def account_update(self, operation, path, value, _from, retry_count=5, retry_wait=2):
#        while (retry_count > 0):
#            print(f"Retry #{retry_count}")
#            try:
                patchOperations=[{
                                    'op'   : operation,  #'add'|'remove'|'replace'|'move'|'copy'|'test',
                                 'path' : path     ,
                                 'value': value    ,
                                 'from' : _from
                              }]
                return self.api_gateway().update_account(patchOperations=patchOperations)
#            except Exception as error:
#                print(f"error: {error}")
#            retry_count -= 1

    def api_keys(self, index_by='id',include_values=False):
        return self._call_method_return_items(method_name="get_api_keys", params={'includeValues':include_values}, index_by=index_by)

    def api_key(self, api_key, include_value=False):
        try:
            return self.api_gateway().get_api_key(apiKey=api_key,includeValue=include_value)
        except:
            return None

    def api_key_create(self,key_name, enabled=True):
        return self.api_gateway().create_api_key(name=key_name,enabled=enabled)

    def api_key_delete(self, key_id_or_name):
        if self.api_key_exists(key_id_or_name):                                     # see if it an api_key value
            self.api_gateway().delete_api_key(apiKey=key_id_or_name)
            return True

        for key_id, value in self.api_keys().items():                           # try to find api_key value
            if value.get('name') == key_id_or_name:                             # via its name
                self.api_gateway().delete_api_key(apiKey=key_id)
                return True
        return False

    def api_key_exists(self, api_key):
        if self.api_key(api_key):
            return True
        return False

    def deployments(self, api_id):
        return self._call_method_return_items(method_name="get_deployments", params={'restApiId':api_id})

    def deployment_create(self, api_id, stage):
        params = {'restApiId': api_id,
                  'stageName': stage}
        return self._call_method('create_deployment',params)

    def domain_name_add_path_mapping(self, rest_api_id, domain_name, base_path, stage='prod'):
        try:
            params = { 'domainName' : domain_name ,
                       'basePath'   : base_path   ,
                       'restApiId'  : rest_api_id ,
                       'stage'      : stage       }
            return self.api_gateway().create_base_path_mapping(**params)
        except Exception as error:
            return {'error': f'{error}'}
    def domain_name_create__regional(self, domain_name, certificate_arn):
        try:
            params = { 'domainName'    : domain_name,
                       'regionalCertificateArn': certificate_arn,
                       'endpointConfiguration': { 'types': ['REGIONAL'] },
                       'securityPolicy'    :'TLS_1_2'}
            return self.api_gateway().create_domain_name(**params)
        except Exception as error:
            return {'error':  f'{error}'}

    def domain_name_delete(self, domain_name):
        try:
            return self.api_gateway().delete_domain_name(domainName=domain_name)
        except Exception as error:
            return {'error':  f'{error}'}

    def domain_names(self, index_by=None):
        return self._index_by(self.api_gateway().get_domain_names().get('items'), index_by=index_by)

    def integration(self, api_id, resource_id, http_method):
        return self.api_gateway().get_integration(restApiId=api_id, resourceId=resource_id, httpMethod=http_method)

    def integration_create__http(self, api_id, resource_id, uri, http_method='GET', integration_http_method='GET'):
        input_type        = 'HTTP'
        try:
            return self.api_gateway().put_integration(restApiId=api_id,
                                                    resourceId=resource_id,
                                                    httpMethod=http_method,
                                                    integrationHttpMethod=integration_http_method,
                                                    type=input_type,
                                                    uri=uri)
        except Exception as error:
            return f'{error}'

    def integration_create__lambda(self, api_id, resource_id, lambda_name, http_method):
        iam         = IAM()
        aws_acct_id = iam.account_id()
        aws_region  = iam.region()

        input_type = 'AWS_PROXY'
        uri = f'arn:aws:apigateway:{aws_region}:lambda:path/2015-03-31/functions/arn:aws:lambda:{aws_region}:{aws_acct_id}:function:{lambda_name}/invocations'
        integration_http_method = 'POST'
        try:
            return self.api_gateway().put_integration(restApiId=api_id, resourceId=resource_id, httpMethod=http_method,
                                                    integrationHttpMethod=integration_http_method,type=input_type, uri=uri)
        except Exception as error:
            return f'{error}'

    def integration_add_permission_to_lambda(self,api_id, lambda_name):
        # create permission to allow lambda function to be invoked by API Gateway
        iam           = IAM()
        aws_acct_id   = iam.account_id()
        aws_region    = iam.region()
        aws_lambda    = Lambda(lambda_name)
        function_arn  = aws_lambda.function_arn()#'gw_bot.lambdas.dev.hello_world'
        statement_id  = 'allow-api-gateway-invoke'
        action        = 'lambda:InvokeFunction'
        principal     = 'apigateway.amazonaws.com'
        source_arn    = f'arn:aws:execute-api:{aws_region}:{aws_acct_id}:{api_id}/*/GET/'

        aws_lambda.permission_delete(function_arn, statement_id) # remove in case there was already a permission with this name
        return aws_lambda.permission_add(function_arn, statement_id, action, principal, source_arn)

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
            return self.api_gateway().get_method(restApiId=api_id, resourceId= resource_id, httpMethod= http_method)
        except Exception as error:
            return {'error': f'{error}'}

    def method_create(self, api_id, resource_id, http_method, authorization_type='NONE'):
        return self._call_method("put_method", { 'restApiId': api_id, 'resourceId':resource_id, 'httpMethod':http_method, 'authorizationType':authorization_type})
#        return self.api_gateway().put_method(restApiId=api_id, resourceId=resource_id, httpMethod=http_method, authorizationType=authorization_type)

    def method_delete(self, api_id, resource_id, http_method):
        return self.api_gateway().delete_method(restApiId=api_id, resourceId=resource_id, httpMethod=http_method)

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


    def stage(self, api_id, stage_name):
        return self._call_method("get_stage", {'restApiId' : api_id, 'stageName':stage_name})

    def stage_url(self,api_id, region, stage, resource=''):
        return f'https://{api_id}.execute-api.{region}.amazonaws.com/{stage}/{resource}'

    def stages(self, api_id, index_by='deploymentId'):
       return self._get_using_api_id('stages', api_id, index_by=index_by, data_key='item')


    #def stages(self, api_id, index_by='deploymentId'):
    #    return self._call_method_return_items(method_name="get_stages", params={'restApiId':api_id},index_by=index_by)

    def resource(self, api_id, path):
        return self.resources(api_id, index_by='path').get(path,{})

    def resource_id(self, api_id, path):
        return self.resource(api_id,path).get('id')

    def resource_methods(self, api_id, path):
        return list(set(self.resource(api_id,path).get('resourceMethods',[])))

    def resource_create(self, api_id, parent_id, path):
        return self.api_gateway().create_resource(restApiId=api_id, parentId=parent_id,pathPart=path)

    def resource_delete(self, api_id, resource_id):
        return self.api_gateway().delete_resource(restApiId=api_id, resourceId=resource_id)

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
        return self.api_gateway().create_rest_api(**params)              # if not, create it

    def rest_api_delete(self, api_id):
        if self.rest_api_exists(api_id):
            self.api_gateway().delete_rest_api(restApiId=api_id)
        return self.rest_api_not_exists(api_id)

    def rest_api_exists(self, api_id):
        return api_id and self.rest_api_info(api_id).get('id') == api_id

    def rest_api_id(self, api_name):
        return self.rest_api(api_name).get('id')

    def rest_api_info(self, api_id):
        try:
            return self.api_gateway().get_rest_api(restApiId=api_id)
        except Exception as error:
            return {'error': f'{error}'}

    def rest_api_not_exists(self, api_id):
        return self.rest_api_exists(api_id) is False

    def rest_apis(self, index_by='id'):
        return self._call_method_return_items(method_name="get_rest_apis",index_by=index_by)

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

    def usage_plan_keys(self, usage_plan_id):
        return self._get('usage_plan_keys', {'usagePlanId':usage_plan_id})


    def usage_plan_add_key(self,usage_plan_id, key_id):

         return self._call_method('create_usage_plan_key', { 'usagePlanId': usage_plan_id,
                                                             'keyId'      : key_id,
                                                             'keyType'    : 'API_KEY'})
    def usage_plan_id(self, usage_plan_name):
        return self.usage_plans(index_by='name').get(usage_plan_name,{}).get('id')

    def usage_plan_remove_key(self, usage_plan_id, key_id):
         return self._call_method('delete_usage_plan_key', { 'usagePlanId': usage_plan_id,
                                                             'keyId'      : key_id       })

    def usage_plans(self, index_by='id'):
        return self._get('usage_plans', index_by=index_by)

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
