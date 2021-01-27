import json

from osbot_utils.decorators.lists.index_by import index_by
from osbot_utils.decorators.methods.cache import cache
from osbot_utils.decorators.methods.catch import catch
from osbot_utils.decorators.methods.remove_return_value import remove_return_value

from osbot_aws.apis.Session import Session
from osbot_aws.apis.S3 import S3
from osbot_utils.utils.Misc import get_missing_fields, wait


class Lambda:
    def __init__(self, name=''):
        self.runtime        = 'python3.8'
        self.memory         = 10240                             # 10 Gb (current AWS limit in Dec 2020)
        self.timeout        = 900                               # 15 M
        self.trace_mode     = 'PassThrough'                     # x-rays disabled
        self.original_name  = name
        self.handler        = name + '.run'
        self.name           = name.replace('.','_')
        self.folder_code    = None
        self.image_uri      = None                          # when using container images
        self.role           = None
        self.s3_bucket      = None
        self.s3_key         = None
        self.layers         = None
        self.env_variables  = None

    # cached dependencies

    @cache
    def client(self):
        return Session().client('lambda')

    @cache
    def s3(self):
        return S3()

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

    def create(self):
        missing_fields = get_missing_fields(self,['name', 'runtime', 'role','handler', 'memory','timeout','s3_bucket', 's3_key'])
        if len(missing_fields) > 0:
            return { 'error': 'missing fields in create_function: {0}'.format(missing_fields) }

        (name, runtime, role, handler, memory_size, timeout, tracing_config, code, layers, environment, package_type) = self.create_params()

        if self.exists() is True:
            return {'status': 'warning', 'name': self.name, 'data': 'lambda function already exists'}

        if self.image_uri:
            pass
        elif self.s3().file_exists(code.get('S3Bucket'), code.get('S3Key')) is False:
            return {'status': 'error', 'name': self.name, 'data': 'could not find provided s3 bucket and s3 key'}

        try:
            kwargs = {'FunctionName'  : name           ,
                      'Role'          : role           ,

                      'MemorySize'    : memory_size    ,
                      'Timeout'       : timeout        ,
                      'TracingConfig' : tracing_config ,
                      'PackageType'   : package_type   ,
                      'Code'          : code           }

            if package_type == 'Zip':
                kwargs['Runtime'] = runtime
                kwargs['Handler'] = handler
            if layers      : kwargs['Layers'     ] = layers
            if environment : kwargs['Environment'] = environment

            data = self.client().create_function(**kwargs)

            return { 'status': 'ok', 'name': self.name , 'data' : data }
        except Exception as error:
            return {'status': 'error', 'data': '{0}'.format(error)}

    @remove_return_value('ResponseMetadata')
    def configuration(self):
        return self.client().get_function_configuration(FunctionName=self.name)
        #return self.info().get('Configuration')

    def configuration_update(self,**kvargs):
        return self.client().update_function_configuration(FunctionName=self.name,**kvargs)

    def create_params(self):
        FunctionName  = self.name
        Runtime       = self.runtime
        Role          = self.role
        Handler       = self.handler
        MemorySize    = self.memory
        Timeout       = self.timeout
        Layers        = self.layers
        Environment   = {'Variables': self.env_variables} if self.env_variables else None
        TracingConfig = { 'Mode': self.trace_mode }

        if self.image_uri:
            Code        = {'ImageUri': self.image_uri}
            PackageType = "Image"
        else:
            Code        = {"S3Bucket": self.s3_bucket, "S3Key": self.s3_key}
            PackageType = "Zip"

        #todo refactor the return value below into an object
        return FunctionName, Runtime, Role, Handler, MemorySize, Timeout, TracingConfig, Code, Layers, Environment, PackageType

    def delete(self):
        if self.exists() is False:
            return False
        self.client().delete_function(FunctionName=self.name)
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

    def exists(self):
        try:
            self.info()
            return True
        except:
            return False

    @cache
    def function_Arn(self):
        return self.info().get('Configuration').get('FunctionArn')

    @remove_return_value('ResponseMetadata')
    def info(self):
        return self.client().get_function(FunctionName=self.name)

    def invoke_raw(self, payload = None):
        try:
            if payload is None: payload = {}
            response      = self.client().invoke(FunctionName=self.name, Payload = json.dumps(payload))

            result_bytes  = response.get('Payload').read()
            result_string = result_bytes.decode('utf-8')
            result        = json.loads(result_string)
            return { 'status': 'ok'   , 'name': self.name, 'data' : result , 'response': response }
        except Exception as error:
            return { 'status': 'error', 'name': self.name, 'data' : '{0}'.format(error) }

    def invoke(self, payload = None):
        if payload is None: payload = {}
        result = self.invoke_raw(payload)
        if result.get('status') == 'ok':
            return result.get('data')
        return {'error': result.get('data')}

    def invoke_async(self, payload = None):
        if payload is None: payload = {}
        return self.client().invoke(FunctionName=self.name, Payload=json.dumps(payload), InvocationType='Event')

    @index_by
    def functions(self):
        return self._call_method_with_paginator('list_functions', 'Functions')


    def permission_add(self, function_arn, statement_id, action, principal, source_arn=None):
        try:
            params = {  'FunctionName': function_arn,
                        'StatementId' : statement_id,
                        'Action'      : action,
                        'Principal'   : principal }
            if source_arn:
                params['SourceArn'] = source_arn
            return self.client().add_permission(**params)
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


    def upload(self):
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
        return self.client().update_function_code(FunctionName = self.name,
                                                  S3Bucket     = self.s3_bucket,
                                                  S3Key        = self.s3_key)

    def update_lambda_configuration(self):
        kwargs = {}
        if self.layers:
            kwargs['Layers'] = self.layers
        if self.env_variables:
            kwargs['Environment'] = {'Variables': self.env_variables}
        if kwargs != {}:
            kwargs['FunctionName'] = self.name
            return self.client().update_function_configuration(**kwargs)


    def wait_for_state(self, state, max_wait_count=40, wait_interval=1):
        for i in range(0, max_wait_count):
            info = self.info()
            state = info.get('Configuration').get('State')
            if state == 'state':
                return {"status" : "ok", "message": f"Status '{state}' was found after {i} * {wait_interval} seconds"}
            wait(wait_interval)
        return {"status" : "error", "message": f"Status '{state}' did not occur in {i} * {wait_interval} seconds"}

    def wait_for_state_active(self, **kwargs):
        return self.wait_for_state("Active", **kwargs)
