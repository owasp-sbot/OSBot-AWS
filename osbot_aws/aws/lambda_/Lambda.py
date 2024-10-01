import json


from osbot_utils.base_classes.Type_Safe                 import Type_Safe
from osbot_utils.utils.Lists                            import unique
from osbot_utils.utils.Json                             import json_loads, json_parse
from osbot_utils.decorators.lists.group_by              import group_by
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from osbot_aws.apis.Logs                                import Logs
from osbot_utils.decorators.lists.index_by              import index_by
from osbot_utils.decorators.methods.catch               import catch
from osbot_utils.decorators.methods.remove_return_value import remove_return_value
from osbot_aws.apis.Session                             import Session
from osbot_aws.aws.s3.S3                                import S3
from osbot_utils.utils.Misc                             import wait, random_string, base64_to_str, list_set, wait_for
from osbot_utils.utils.Status                           import status_ok, status_error, status_warning
from osbot_aws.aws.session.Session__Kwargs__Lambda      import Session__Kwargs__Lambda
from osbot_aws.aws.session.Session__Kwargs__S3          import Session__Kwargs__S3


class Lambda(Type_Safe):
    session_kwargs__lambda: Session__Kwargs__Lambda
    session_kwargs__s3    : Session__Kwargs__S3


    def __init__(self, name='', **kwargs):
        super().__init__(**kwargs)
        self.architecture   = 'x86_64'                          # other option is 'arm64'
        self.runtime        = 'python3.11'
        self.memory         = 512                               # default to 512Mb max is 10,000 Mb (current AWS limit in Dec 2020)
        self.timeout        = 60                                # default to 60 secs (1m) max is 900 secs (15m)
        self.trace_mode     = 'PassThrough'                     # x-rays disabled
        self.original_name  = name
        self.handler        = name + '.run'
        self.name           = name.replace('.','_')
        self.folder_code    = None
        self.image_uri      = None                              # when using container images
        self.role           = None
        self.s3_bucket      = None
        self.s3_key         = None
        self.layers         = None
        self.env_variables  = None
        self.tags           = {}

    # cached dependencies

    @cache_on_self
    def client(self):
        return Session().client(**self.session_kwargs__lambda.__locals__())

    @cache_on_self
    def s3(self):
        return S3(session_kwargs__s3=self.session_kwargs__s3.__locals__())

    # helper methods

    #@staticmethod
    # def invoke_using_paginator(api, method, field_id, **kwargs):
    #     paginator = api.get_paginator(method)
    #     for page in paginator.paginate(**kwargs):
    #         for id in page.get(field_id):
    #             yield id

    def _call_method_with_paginator(self, method, field_id, **kwargs):
        api       = self.client()
        paginator = api.get_paginator(method)
        for page in paginator.paginate(**kwargs):
            for id in page.get(field_id):
                yield id

    # main methods

    def add_layer(self, layer_arn=None):
        if layer_arn:
            if self.layers is None:
                self.layers = []
            self.layers.append(layer_arn)
            self.layers = unique(self.layers)           # make sure there are no duplicates
        return self

    def add_layers(self, layers_arn):
        for layer_arn in layers_arn:
            self.add_layer(layer_arn)
        return self

    def account_settings(self):
        return self.client().get_account_settings()

    @catch
    @remove_return_value(field_name='ResponseMetadata')
    def alias(self, function_name, name):
        return self.client().get_alias(FunctionName=function_name, Name=name)

    @catch
    def alias_create(self, function_name, function_version, name, description):
        return self.client().create_alias(FunctionName=function_name,FunctionVersion= function_version,Name=name, Description=description)

    @catch
    @remove_return_value(field_name='ResponseMetadata')
    def alias_delete(self, function_name, name):
        return self.client().delete_alias(FunctionName=function_name, Name=name)

    @index_by
    def aliases(self,function_name):
        return self.client().list_aliases(FunctionName=function_name).get('Aliases')

    @remove_return_value('ResponseMetadata')
    def configuration(self):
        return self.client().get_function_configuration(FunctionName=self.name)

    def configuration_update(self,**kvargs):
        return self.client().update_function_configuration(FunctionName=self.name,**kvargs)

    def create(self):
        kwargs = self.create_kwargs()
        kwargs_status = self.validate_create_kwargs(kwargs)
        if kwargs_status.get('status') != 'ok':
            return kwargs_status
        try:
            data = self.client().create_function(**kwargs)
            return { 'status': 'ok', 'name': self.name , 'data' : data }
        except Exception as error:
            return {'status': 'error', 'error': '{0}'.format(error), 'data': kwargs}

    def create_kwargs(self):
        kwargs = {  'Architectures' : [self.architecture]                                , # no idea why this is an array since we get an exception when there is more than one value
                    'FunctionName'  : self.name or  random_string(prefix='temp_lambda_') ,
                    'MemorySize'    : self.memory                                        ,
                    'Role'          : self.role                                          ,
                    'Timeout'       : self.timeout                                       ,
                    'TracingConfig' : { 'Mode': self.trace_mode }                        ,
                    'Tags'          : self.tags                                          }

        if self.env_variables:
            kwargs['Environment'] = {'Variables': self.env_variables}
        if self.image_uri:
            kwargs['Code'         ] = {'ImageUri': self.image_uri}
            kwargs['PackageType'  ] = "Image"
        else:
            kwargs['Code'          ] = {"S3Bucket": self.s3_bucket, "S3Key": self.s3_key}
            kwargs['PackageType'   ] = "Zip"
            kwargs['Runtime'       ] = self.runtime
            kwargs['Handler'       ] = self.handler

        if self.layers:
            kwargs['Layers'] = self.layers

        return kwargs


    def delete(self, delete_log_group=True):                # todo  Delete Lambda function method should also delete cloud formation logs #6 (https://github.com/owasp-sbot/OSBot-AWS/issues/6)
        if self.exists() is False:
            return False
        self.client().delete_function(FunctionName=self.name)
        if delete_log_group:
            self.log_group().group_delete()
        return self.exists() is False

    @catch
    def event_source_create(self, event_source_arn, function_name):
        return self.client().create_event_source_mapping(EventSourceArn=event_source_arn, FunctionName=function_name)

    @catch
    def event_source_delete(self, event_source_uuid):
        return self.client().delete_event_source_mapping(UUID=event_source_uuid)

    @catch
    @index_by
    def event_sources(self):
        return self.client().list_event_source_mappings().get('EventSourceMappings')

    def exists(self, function_name=None):
        try:
            return self.info(function_name or self.name) is not None
        except:
            return False

    @cache_on_self
    def function_arn(self):
        return self.info().get('Configuration').get('FunctionArn')

    def function_url(self, function_alias=None):
        return self.function_url_info(function_alias).get('FunctionUrl')

    def function_set_policy_to_allow_public_access(self):
        function_arn = self.function_arn()
        auth_type    = 'NONE'
        statement_id = 'FunctionURLAllowPublicAccess'
        if statement_id in self.policy_statements(index_by='Sid') :
            self.permission_delete(function_arn, statement_id)

        kwargs = { 'statement_id'          : statement_id                  ,
                   'action'                : 'lambda:InvokeFunctionUrl'    ,
                   'function_url_auth_type': auth_type                     ,
                   'function_arn'          : function_arn                  ,
                   'principal'             : '*'                           }

        return self.permission_add(**kwargs)

    def function_url_exists(self, function_alias=None):
        return self.function_url_info(function_alias) != {}

    def function_url_info(self, function_alias=None):
        try:
            kwargs = dict(FunctionName= self.function_arn())
            if function_alias:
                kwargs['Qualifier'] = function_alias

            return self.client().get_function_url_config(**kwargs)
        except Exception:                                  # todo: refactor to confirm exception is botocore.errorfactory.ResourceNotFoundException (which is not exposed)
            return {}

    def function_url_delete(self, function_alias=None):
        if self.function_url_exists(function_alias):
            kwargs = dict(FunctionName= self.function_arn())
            if function_alias:
                kwargs['Qualifier'] = function_alias

            return self.client().delete_function_url_config(**kwargs)

    @remove_return_value('ResponseMetadata')
    def function_url_create(self, function_alias=None, auth_type="AWS_IAM", cors=None, invoke_mode='BUFFERED'):
        if self.function_url_exists(function_alias) is False:
            function_arn   = self.function_arn()
            auth_type      = auth_type #'NONE',
            cors           = cors or {}
            invoke_mode    = invoke_mode # 'RESPONSE_STREAM'
            kwargs         = dict(FunctionName = function_arn   ,
                                  AuthType     = auth_type      ,
                                  Cors         = cors           ,
                                  InvokeMode   = invoke_mode    )
            if function_alias:
                kwargs['Qualifier'] = function_alias

            return self.client().create_function_url_config(**kwargs)
        return {"status": "warning", "message": "function url already existed"}

    def function_url_create_with_public_access(self, invoke_mode='BUFFERED'):
        function_url_create     = self.function_url_create(auth_type='NONE', invoke_mode=invoke_mode)
        self.wait_for_function_update_to_complete()
        function_set_policy     = self.function_set_policy_to_allow_public_access()
        self.wait_for_function_update_to_complete()
        return dict(function_url_create=function_url_create, function_set_policy=function_set_policy)

    def function_url_update(self, function_alias=None, auth_type=None, cors=None, invoke_mode=None):
        if self.function_url_exists(function_alias) :
            function_arn   = self.function_arn()

            kwargs         = dict(FunctionName = function_arn)

            if function_alias:
                kwargs['Qualifier'] = function_alias
            if auth_type:
                kwargs['AuthType'] = auth_type
            if cors:
                kwargs['Cors'] = cors
            if invoke_mode:
                kwargs['InvokeMode'] = invoke_mode

            return self.client().update_function_url_config(**kwargs)

    # todo: add this policy when creating a function url with NONE auth_type

    # {
    #   "Version": "2012-10-17",
    #   "Statement": [
    #     {
    #       "StatementId": "FunctionURLAllowPublicAccess",
    #       "Effect": "Allow",
    #       "Principal": "*",
    #       "Action": "lambda:InvokeFunctionUrl",
    #       "Resource": "{function_arn}",
    #       "Condition": {
    #         "StringEquals": {
    #           "lambda:FunctionUrlAuthType": "NONE"
    #         }
    #       }
    #     }
    #   ]
    # }
    @remove_return_value('ResponseMetadata')
    def info(self, function_name=None):
        return self.client().get_function(FunctionName=function_name or self.name)

    def invoke_raw(self, payload = None, client_context=None, log_type='None', qualifier=None):
        try:
            kwargs = { "FunctionName" : self.name                 ,
                       "Payload"      : json.dumps(payload or {}) ,
                       'LogType'      : log_type                  }
            if client_context:
                kwargs['ClientContext'] = client_context
            if qualifier:
                kwargs['Qualifier'    ] = qualifier

            response      = self.client().invoke(**kwargs)

            result_bytes  = response.get('Payload').read()
            result_string = result_bytes.decode('utf-8')
            result        = json_loads(result_string)
            if result == {}:
                result = {'raw_message': result_string}
            return { 'status': 'ok'   , 'name': self.name, 'data' : result , 'response': response }
        except Exception as error:
            return { 'status': 'error', 'name': self.name, 'data' : '{0}'.format(error) }

    def invoke(self, payload = None):
        result = self.invoke_raw(payload)
        if result.get('status') == 'ok':
            return result.get('data')
        return {'error': result.get('data')}

    def invoke_async(self, payload = None):
        kwargs = { "FunctionName"  : self.name                  ,
                   "Payload"       : json.dumps(payload or {})  ,
                   "InvocationType": 'Event'                    }
        return self.client().invoke(**kwargs)

    def invoke_dry_run(self, payload = None):
        kwargs = { "FunctionName"  : self.name                  ,
                   "Payload"       : json.dumps(payload or {})  ,
                   "InvocationType": 'DryRun'                   }
        return self.client().invoke(**kwargs)

    def invoke_return_logs(self, payload=None):
        result                   = self.invoke_raw(payload=payload, log_type='Tail')
        if result.get('status') == 'error':
            return result
        logs                     = result.get('response', {}).get('LogResult', '')
        result['execution_logs'] = base64_to_str(logs, encoding='utf-8')
        result['return_value'  ] = result.get('data')
        result['request_id'    ] = result.get('response', {}).get('ResponseMetadata',{}).get('RequestId')
        del result['data'    ]
        del result['response']
        return result

    @index_by
    def functions(self):
        return list(self._call_method_with_paginator('list_functions', 'Functions'))

    @index_by
    def functions_names(self):
        return list_set(self.functions(index_by='FunctionName'))

    def log_group(self):
        return Logs(group_name=f'/aws/lambda/{self.name}')

    def permission_add(self, function_arn, statement_id, action, principal, source_arn=None, function_url_auth_type=None):
        try:
            params = {  'FunctionName': function_arn,
                        'StatementId' : statement_id,
                        'Action'      : action,
                        'Principal'   : principal }
            if source_arn             : params['SourceArn'          ] = source_arn
            if function_url_auth_type : params['FunctionUrlAuthType'] = function_url_auth_type

            result = self.client().add_permission(**params)
            if type(result.get('Statement')) is str:
                return json_parse(result.get('Statement'))
            return result
        except Exception as error:
            return {'error': f'{error}'}

    def permission_delete(self, function_name, statement_id):
        try:
            params = {  'FunctionName': function_name,
                        'StatementId' : statement_id,                        }
            return self.client().remove_permission(**params)
        except Exception as error:
            return {'error': f'{error}'}

    def permissions(self):
        return self.policy().get('Statement',[])


    def shell(self):
        from osbot_aws.apis.shell.Shell_Client import Shell_Client                  # todo: see way to solve circular dependency
        return Shell_Client(self)

    def shell_python_exec(self, code, auth_key):  # this needs @lambda_shell on the Lambda's run method
        params = {'lambda_shell': {'method_name':'python_exec', 'method_kwargs': {'code' : code} ,'auth_key' : auth_key }}
        return self.invoke(params)

    @catch
    def policy(self):
        try:
            policy_str = self.client().get_policy(FunctionName=self.name).get('Policy')
            return json.loads(policy_str)
        except:                 # ResourceNotFoundException doesn't seem to exposed to we have to do a global capture
            return {}

    @index_by
    @group_by
    def policy_statements(self):
        return self.policy().get('Statement', [])

    def policy_statements_clear(self):
        function_arn = self.function_arn()
        for statement in self.policy_statements():
            statement_id = statement.get('Sid')
            self.permission_delete(function_name=function_arn, statement_id=statement_id)
        return self

    def set_handler             (self, value): self.handler        = value    ; return self
    def set_role                (self, value): self.role           = value    ; return self
    def set_s3_bucket           (self, value): self.s3_bucket      = value    ; return self
    def set_s3_key              (self, value): self.s3_key         = value    ; return self
    def set_folder_code         (self, value): self.folder_code    = value    ; return self
    def set_trace_mode          (self, value): self.trace_mode     = value    ; return self
    def set_layers              (self, value): self.layers         = value    ; return self
    def set_env_variables       (self, value): self.env_variables  = value    ; return self
#    def set_xrays_on            (self       ): self.trace_mode  = 'Active' ; return self

    # def set_s3_bucket_and_key(self, s3_bucket, s3_key):
    #     self.set_s3_bucket(s3_bucket)
    #     self.set_s3_key   (s3_key   )
    #     return self

    def set_env_variable(self, key, value):
        if self.env_variables is None:
            self.env_variables = {}
        self.env_variables[key] = value
        return self

    def upload(self):
        if self.image_uri is None:              # only upload when not using image_uri                                              # don't need to upload when running lambda from a container
            self.s3().folder_upload(self.folder_code, self.s3_bucket, self.s3_key)
            return self.s3().file_exists(self.s3_bucket, self.s3_key)

    def update(self):
        if self.exists() is False:
            self.upload()
            return self.create()
        else:
            self.upload()
        try:
            update_code_result   = self.update_lambda_code()
            update_config_result = self.update_lambda_configuration()
            return {'status': 'ok'    , 'name': self.name, 'data': {"update_code": update_code_result, "update_config": update_config_result}}

        except Exception as error:
            return { 'status': 'error', 'name': self.name, 'data': '{0}'.format(error)}

    def update_lambda_code(self):
        self.wait_for_function_update_to_complete()
        if self.image_uri:
            update_kwargs = dict(FunctionName = self.name     ,
                                 ImageUri     = self.image_uri)
        else:
            update_kwargs = dict(FunctionName = self.name     ,
                                 S3Bucket     = self.s3_bucket,
                                 S3Key        = self.s3_key   )

        return self.client().update_function_code(**update_kwargs)

    def update_lambda_image_uri(self, image_uri):
        self.wait_for_function_update_to_complete()
        self.image_uri = image_uri
        return self.client().update_function_code(FunctionName = self.name     ,
                                                  ImageUri     = self.image_uri)

    def update_lambda_configuration(self):
        self.wait_for_function_update_to_complete()         # make sure there is no update also happening at this time
        kwargs = {}
        if self.layers:
            kwargs['Layers'] = self.layers
        if self.env_variables:
            kwargs['Environment'] = {'Variables': self.env_variables}
        if kwargs != {}:
            kwargs['FunctionName'] = self.name
            return self.client().update_function_configuration(**kwargs)

    def validate_create_kwargs(self, kwargs):
        name      = kwargs.get('FunctionName'    )
        code      = kwargs.get('Code'        , {})
        image_uri = code  .get('ImageUri'        )
        s3_bucket = code  .get('S3Bucket'        )
        s3_key    = code  .get('S3Key'           )

        if len(name) > 64:
            return status_error(message="lambda functions name cannot be bigger than 64 chars", data=self.name)
        if self.exists(function_name=name):
            return status_warning(message=f'lambda function already exists: {name}')

        if image_uri is None:
            if self.s3().file_not_exists(s3_bucket, s3_key):
                return status_error(message=f'for function {name}, could not find provided s3 bucket and s3 key: {s3_bucket} {s3_key}')
        return status_ok(message='validated ok  the lambda create_kwargs')

    def wait_for_function_update_to_complete(self, max_attempts=40, wait_time=0.1):
        status = None
        for i in range(max_attempts):
            configuration = self.configuration()
            status        = configuration.get('LastUpdateStatus')
            if status == 'Successful':
                #print(f"\n after  {i} attempts, update completed successfully")
                break
            status = configuration.get('State')         # helps to debug when the update fails
            wait_for(wait_time)
        return status

    def wait_for_state(self, state, max_wait_count=40, wait_interval=1):
        for i in range(0, max_wait_count):
            info = self.info()
            current_state = info.get('Configuration').get('State')
            if current_state == state:
                return {"status" : "ok", "message": f"Status '{state}' was found after {i} * {wait_interval} seconds"}
            wait(wait_interval)
        return {"status" : "error", "message": f"Status '{state}' did not occur in {i} * {wait_interval} seconds"}

    def wait_for_state_active(self, **kwargs):
        return self.wait_for_state("Active", **kwargs)

def invoke_lambda(lambda_name, payload):
    return Lambda(name=lambda_name).invoke(payload)

def invoke_lambda_async(lambda_name, payload):
    return Lambda(name=lambda_name).invoke_async(payload)
