import shutil
import sys
from    distutils.dir_util  import copy_tree
from    os.path             import join,abspath
from    pbx_gs_python_utils.utils.Files         import Files
from    pbx_gs_python_utils.utils.aws.Aws_Cli   import Aws_Cli
from    pbx_gs_python_utils.utils.aws.s3        import S3


class Lambdas:
    def __init__(self,name, handler = None, memory = None, timeout = None, path_libs = None, runtime = None, **kwargs):
        self.aws = Aws_Cli(**kwargs)
        # default values
        self.role       = 'arn:aws:iam::244560807427:role/lambda_with_s3_access'
        self.s3_bucket  = 'gs-lambda-tests'
        self.source     = abspath(join(__file__,'../../..'))
        if path_libs:
            self.path_libs = abspath(join(self.source,path_libs))
        else:
            self.path_libs = None
        if runtime:
            self.runtime = runtime
        else:
            self.runtime = 'python3.6'


        # values expected to be provided
        self.original_name  = name
        self.name           = name.replace('.','_')
        if handler is not None:
            self.handler = handler
        else:
            self.handler = '{0}.run'.format(name)

        self.s3_key     = 'dinis/lambdas/{0}.zip'.format(self.name)

        if memory is not None:
            self.memory = memory
        else:
            self.memory = 1024
        if timeout is not None:
            self.timeout = timeout
        else:
            self.timeout = 60

        # starting to move values to kwargs
        if kwargs.get('bucket'): self.s3_bucket = kwargs['bucket']


    def create(self, upload_source = True):
        if upload_source:
            self.aws.s3_upload_folder(self.source, self.s3_bucket, self.s3_key)
        self.aws.lambda_create_function(self.name, self.role, self.handler, self.s3_bucket, self.s3_key, self.memory, self.timeout, runtime = self.runtime)
        return self

    def delete(self):
        self.aws.lambda_delete_function(self.name)
        return self

    # def delete_local_zip(self):
    #     os.remove(self.zip_file)
    #     return self

    def exists(self):
        return self.aws.lambda_function_exists(self.name)

    def function_Arn(self):
        return self.info().get('Configuration').get('FunctionArn')

    def info(self):
        return self.aws.lambda_function_info(self.name)

    def invoke(self, payload = {}):
        (result, response) = self.aws.lambda_invoke_function(self.name, payload)
        return result

    def invoke_async(self, payload = {}):
        return self.aws.lambda_invoke_function_async(self.name, payload)

    def upload(self):
        #if self.path_libs is None:
        #    self.aws.s3_upload_folder(self.source, self.s3_bucket, self.s3_key)
        #else:
            #copy_tree(self.source, self.path_libs)  # for now copy all files into dependencies folders (need to improve this by using temp folders)

        self.aws.s3_upload_folder(self.source, self.s3_bucket, self.s3_key)
        print(self.s3_bucket, self.s3_key)
        return self

    def upload_and_invoke(self, payload = {}):
        return self.update_with_src().invoke(payload)

    def update(self):
        if (self.exists() is False):
            return self.upload().create(upload_source = False)

        self.upload().aws.lambda_update_function(self.name, self.s3_bucket, self.s3_key)
        return self

    def update_with_lib(self):
        src_tmp     = '/tmp/src_{0}'.format(self.original_name.split('.').pop())  # there were a couple issues with long folder names
        Files.folder_delete_all(src_tmp)
        src_tmp_lib = '{0}/pbx_gs_python_utils'.format(src_tmp)
        copy_tree(self.source, src_tmp_lib)
        self.source = src_tmp
        return self.update()

    def update_with_src(self, path_to_src = None):                                   # use this when wanting to add a local folder to the lambda source code
        src_tmp = '/tmp/src_{0}'.format(self.original_name.split('.').pop())  # there were a couple issues with long folder names
        Files.folder_delete_all(src_tmp)
        src_tmp_lib = '{0}/pbx_gs_python_utils'.format(src_tmp)
        copy_tree(self.source, src_tmp_lib)

        if path_to_src is None: path_to_src = Files.path_combine(__file__, '../../../../../../src')
        copy_tree(path_to_src, src_tmp)
        self.source = src_tmp
        return self.update()

def exec_string_in_lambda(lambda_code):
    name = 'lambda_from_string'                  # should make this a random value
    handler = 'lambdas.dev.exec_string.run'
    temp_lambda = Lambdas(name, handler, 3008)
    result      = temp_lambda.upload_and_invoke({"code": lambda_code})
    temp_lambda.delete()
    return result

def invoke_lambda(file, payload):
    return Lambdas(file).upload_and_invoke(payload)

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
    s3.folder_upload(path_libs, s3_bucket, s3_folder)
    return s3.file_exists(s3_bucket, s3_file)
