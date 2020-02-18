import json
import shutil
import sys
from   distutils.dir_util  import copy_tree

import boto3
from    pbx_gs_python_utils.utils.Files         import Files

from osbot_aws.apis.Session import Session
from osbot_aws.helpers.Method_Wrappers import cache, index_by
from osbot_aws.tmp_utils.Temp_Misc import Temp_Misc
from osbot_aws.apis.S3 import S3


class Lambda:
    def __init__(self, name=''):
        self.runtime        = 'python3.7'
        self.memory         = 3008
        self.timeout        = 60
        self.trace_mode     = 'PassThrough'                     # x-rays disabled
        self.original_name  = name
        self.handler        = name + '.run'
        self.name           = name.replace('.','_')
        self.folder_code    = None
        self.role           = None
        self.s3_bucket      = None
        self.s3_key         = None

    # cached dependencies

    @cache
    def boto_lambda(self):
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
        api       = self.boto_lambda()
        paginator = api.get_paginator(method)
        for page in paginator.paginate(**kwargs):
            for id in page.get(field_id):
                yield id


    # main methods


    def add_permission(self, function_arn, statement_id,action,principal,source_arn=None):
        try:
            params = {  'FunctionName': function_arn,
                        'StatementId' : statement_id,
                        'Action'      : action,
                        'Principal'   : principal }
            if source_arn:
                params['SourceArn'] = source_arn
            return self.boto_lambda().add_permission(**params)
        except Exception as error:
            return {'error': f'{error}'}


    def create(self):
        missing_fields = Temp_Misc.get_missing_fields(self,['name', 'runtime', 'role','handler', 'memory','timeout','s3_bucket', 's3_key'])
        if len(missing_fields) > 0:
            return { 'error': 'missing fields in create_function: {0}'.format(missing_fields) }

        (name, runtime, role, handler, memory_size, timeout, tracing_config, code) = self.create_params()

        if self.exists() is True:
            return {'status': 'warning', 'name': self.name, 'data': 'lambda function already exists'}

        if self.s3().file_exists(code.get('S3Bucket'), code.get('S3Key')) is False:
            return {'status': 'error', 'name': self.name, 'data': 'could not find provided s3 bucket and s3 key'}

        try:
            data = self.boto_lambda().create_function(  FunctionName  = name           ,
                                                        Runtime       = runtime        ,
                                                        Role          = role           ,
                                                        Handler       = handler        ,
                                                        MemorySize    = memory_size    ,
                                                        Timeout       = timeout        ,
                                                        TracingConfig = tracing_config ,
                                                        Code          = code)

            return { 'status': 'ok', 'name': self.name , 'data' : data }
        except Exception as error:
            return {'status': 'error', 'data': '{0}'.format(error)}

    def create_params(self):
        FunctionName  = self.name
        Runtime       = self.runtime
        Role          = self.role
        Handler       = self.handler
        MemorySize    = self.memory
        Timeout       = self.timeout
        TracingConfig = { 'Mode': self.trace_mode }
        Code          = { "S3Bucket" : self.s3_bucket, "S3Key": self.s3_key}
        return FunctionName, Runtime, Role, Handler, MemorySize, Timeout, TracingConfig, Code

    def delete(self):
        if self.exists() is False:
            return False
        self.boto_lambda().delete_function(FunctionName=self.name)
        return self.exists() is False

    def delete_permission(self, function_name, statement_id):
        try:
            params = {  'FunctionName': function_name,
                        'StatementId' : statement_id,                        }
            return self.boto_lambda().remove_permission(**params)
        except Exception as error:
            return {'error': f'{error}'}


    def exists(self):
        try:
            self.info()
            return True
        except:
            return False


    def function_Arn(self):
        return self.info().get('Configuration').get('FunctionArn')

    def info(self):
        return self.boto_lambda().get_function(FunctionName=self.name)

    def invoke_raw(self, payload = None):
        try:
            if payload is None: payload = {}
            response      = self.boto_lambda().invoke(FunctionName=self.name, Payload = json.dumps(payload) )

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
        return None

    def invoke_async(self, payload = None):
        if payload is None: payload = {}
        return self.boto_lambda().invoke(FunctionName=self.name, Payload=json.dumps(payload), InvocationType='Event')

    @index_by
    def functions(self):
        return self._call_method_with_paginator('list_functions', 'Functions')

        # data = {}
        # functions = self.invoke_using_paginator(self.boto_lambda(), 'list_functions', 'Functions')
        # for function in functions:
        #     data[function['FunctionName']] = function
        # return data

    def set_role                (self, value): self.role        = value    ; return self
    def set_s3_bucket           (self, value): self.s3_bucket   = value    ; return self
    def set_s3_key              (self, value): self.s3_key      = value    ; return self
    def set_folder_code         (self, value): self.folder_code = value    ; return self
    def set_trace_mode          (self, value): self.trace_mode  = value    ; return self
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
            result = self.update_lambda_code()
            return {'status': 'ok'    , 'name': self.name, 'data': result             }

        except Exception as error:
            return { 'status': 'error', 'name': self.name, 'data': '{0}'.format(error)}

    def update_lambda_code(self):
        return self.boto_lambda().update_function_code(FunctionName = self.name     ,
                                                       S3Bucket     = self.s3_bucket,
                                                       S3Key        = self.s3_key   )