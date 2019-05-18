import json
import shutil
import sys
from   distutils.dir_util  import copy_tree

import boto3
from    pbx_gs_python_utils.utils.Files         import Files

from osbot_aws.apis.Session import Session
from osbot_aws.tmp_utils.Temp_Misc import Temp_Misc
from osbot_aws.apis.S3 import S3


class Lambda:
    def __init__(self, name):
        self.runtime        = 'python3.6'
        self.memory         = 3008
        self.timeout        = 60
        #self.region_name    = 'eu-west-2'
        self.trace_mode     = 'PassThrough'                     # x-rays disabled
        self.original_name  = name
        self.handler        = name + '.run'
        self.name           = name.replace('.','_')
        self.folder_code    = None
        self.role           = None
        self.s3_bucket      = None
        self.s3_key         = None
        self._boto_lambda   = None
        self._s3            = None

    def boto_lambda(self):
        if self._boto_lambda is None:
            self._boto_lambda = Session().client('lambda')  #  region_name=self.region_name)
        return self._boto_lambda

    def s3(self):
        if self._s3 is None:
            self._s3 = S3()
        return self._s3

    # def __init__(self,name, handler = None, memory = None, timeout = None, path_libs = None, runtime = None, **kwargs):
    #     self.aws = Aws_Cli(**kwargs)
    #     # default values
    #     self.role       = 'arn:aws:iam::244560807427:role/lambda_with_s3_access'
    #     self.s3_bucket  = 'gs-lambda-tests'
    #     self.source     = abspath(join(__file__,'../../..'))
    #     if path_libs:
    #         self.path_libs = abspath(join(self.source,path_libs))
    #     else:
    #         self.path_libs = None
    #     if runtime:
    #         self.runtime = runtime
    #     else:
    #         self.runtime = 'python3.6'
    #
    #
    #     # values expected to be provided
    #     self.original_name  = name
    #     self.name           = name.replace('.','_')
    #     if handler is not None:
    #         self.handler = handler
    #     else:
    #         self.handler = '{0}.run'.format(name)
    #
    #     self.s3_key     = 'dinis/lambdas/{0}.zip'.format(self.name)
    #
    #     if memory is not None:
    #         self.memory = memory
    #     else:
    #         self.memory = 1024
    #     if timeout is not None:
    #         self.timeout = timeout
    #     else:
    #         self.timeout = 60
    #
    #     # starting to move values to kwargs
    #     if kwargs.get('bucket'): self.s3_bucket = kwargs['bucket']



    #def create(self, upload_source = True):
        # if upload_source:
        #     self.aws.s3_upload_folder(self.source, self.s3_bucket, self.s3_key)
        # self.aws.lambda_create_function(self.name, self.role, self.handler, self.s3_bucket, self.s3_key, self.memory, self.timeout, runtime = self.runtime)
        # return self

    def create(self): #, name, role, handler, s3_bucket, s3_key, memory = 512, timeout = 25 , runtime = 'python3.6'):
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

    # def delete_local_zip(self):
    #     os.remove(self.zip_file)
    #     return self

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

    def set_role                (self, value): self.role        = value    ; return self
    def set_s3_bucket           (self, value): self.s3_bucket   = value    ; return self
    def set_s3_key              (self, value): self.s3_key      = value    ; return self
    def set_folder_code         (self, value): self.folder_code = value    ; return self
    def set_trace_mode          (self, value): self.trace_mode  = value    ; return self
    def set_xrays_on            (self       ): self.trace_mode  = 'Active' ; return self

    # def set_s3_bucket_and_key(self, s3_bucket, s3_key):
    #     self.set_s3_bucket(s3_bucket)
    #     self.set_s3_key   (s3_key   )
    #     return self


    def upload(self):
        #if self.path_libs is None:
        #    self.aws.s3_upload_folder(self.source, self.s3_bucket, self.s3_key)
        #else:
            #copy_tree(self.source, self.path_libs)  # for now copy all files into dependencies folders (need to improve this by using temp folders)
        self.s3().folder_upload(self.folder_code, self.s3_bucket, self.s3_key)
        return self.s3().file_exists(self.s3_bucket, self.s3_key)

    def upload_and_invoke(self, payload = {}):
        return self.update_with_src().invoke(payload)

    def update(self):
        if self.exists() is False:
            self.upload()
            return self.create()

        self.upload()
        try:
            result = self.boto_lambda().update_function_code(FunctionName= self.name     ,
                                                             S3Bucket    = self.s3_bucket,
                                                             S3Key       = self.s3_key   )
            return {'status': 'ok'    , 'name': self.name, 'data': result             }

        except Exception as error:
            return { 'status': 'error', 'name': self.name, 'data': '{0}'.format(error)}


    # def update_with_lib(self):
    #     src_tmp     = '/tmp/src_{0}'.format(self.original_name.split('.').pop())  # there were a couple issues with long folder names
    #     Files.folder_delete_all(src_tmp)
    #     src_tmp_lib = '{0}/pbx_gs_python_utils'.format(src_tmp)
    #     copy_tree(self.source, src_tmp_lib)
    #     self.source = src_tmp
    #     return self.update()
    #
    # def update_with_src(self, path_to_src = None):                                   # use this when wanting to add a local folder to the lambda source code
    #     src_tmp = '/tmp/src_{0}'.format(self.original_name.split('.').pop())  # there were a couple issues with long folder names
    #     Files.folder_delete_all(src_tmp)
    #     src_tmp_lib = '{0}/pbx_gs_python_utils'.format(src_tmp)
    #     copy_tree(self.source, src_tmp_lib)
    #
    #     if path_to_src is None: path_to_src = Files.path_combine(__file__, '../../../../../../src')
    #     copy_tree(path_to_src, src_tmp)
    #     self.source = src_tmp
    #     return self.update()

# def exec_string_in_lambda(lambda_code):
#     name = 'lambda_from_string'                  # should make this a random value
#     handler = 'lambdas.dev.exec_string.run'
#     temp_lambda = Lambdas(name, handler, 3008)
#     result      = temp_lambda.upload_and_invoke({"code": lambda_code})
#     temp_lambda.delete()
#     return result
#
# def invoke_lambda(file, payload):
#     return Lambdas(file).upload_and_invoke(payload)

def load_dependencies(targets):
    for target in targets:
        load_dependency(target)

def load_dependency(target):
    s3         = S3()
    s3_bucket  = 'gs-lambda-tests'
    s3_key     = 'dinis/lambdas-dependencies/{0}.zip'.format(target)
    tmp_dir    = Files.path_combine('/tmp/lambdas-dependencies', target)

    if s3.file_exists(s3_bucket,s3_key) is False:
        raise Exception("In Lambda load_dependency, could not find dependency for: {0}".format(target))

    if Files.not_exists(tmp_dir):                               # if the tmp folder doesn't exist it means that we are loading this for the first time (on a new Lambda execution environment)
        zip_file = s3.file_download(s3_bucket, s3_key,False)    # download zip file with dependencies
        shutil.unpack_archive(zip_file, extract_dir = tmp_dir)  # unpack them
        sys.path.append(tmp_dir)                                # add tmp_dir to the path that python uses to check for dependencies
    return Files.not_exists(tmp_dir)

def upload_dependency(target):
    s3        = S3()
    s3_bucket = 'gs-lambda-tests'
    s3_folder = 'dinis/lambdas-dependencies/'
    s3_file   = 'dinis/lambdas-dependencies/{0}.zip'.format(target)
    path_libs = Files.path_combine('../../../_lambda_dependencies/', target)
    if Files.not_exists(path_libs):
        raise Exception("In Lambda upload_dependency, could not find dependency for: {0}".format(target))
    s3.folder_upload(path_libs, s3_bucket, s3_file)
    return s3.file_exists(s3_bucket, s3_file)
