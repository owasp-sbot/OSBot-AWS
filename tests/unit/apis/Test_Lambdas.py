import os
import unittest

from pbx_gs_python_utils.utils.Assert import Assert
from pbx_gs_python_utils.utils.Dev import Dev
from pbx_gs_python_utils.utils.Files import Files

from osbot_aws.apis.Lambdas import Lambdas
from osbot_aws.apis.S3 import S3
from osbot_aws.helpers.IAM_Role import IAM_Role

region        = 'eu-west-2'
account_id    ='244560807427'
lambda_name   = 'tmp_lambda_dev_test'
tmp_s3_bucket = 'gs-lambda-tests'
tmp_s3_key    =  'unit_tests/lambdas/{0}.zip'.format(lambda_name)
lambda_code   = """def run(event, context):
                      return 'hello {0}'.format(event.get('name'))"""

class Test_Lambdas(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        lambdas = Lambdas(lambda_name)

    @classmethod
    def tearDownClass(cls):
        lambdas = Lambdas(lambda_name)

    def setUp(self):
        self.lambdas = Lambdas(lambda_name)

    def test__init__(self):
        assert self.lambdas.runtime       == 'python3.6'
        assert self.lambdas.memory        == 3008
        assert self.lambdas.timeout       == 60
        assert self.lambdas.original_name == lambda_name

    def test_create_function__no_params(self):
        assert self.lambdas.create_function() == { 'error': "missing fields in create_function: ['role', 's3_bucket', 's3_key']"}

    def test_create_function__bad_s3_key_(self):
        self.lambdas.set_role('').set_s3_bucket('').set_s3_key('')
        assert self.lambdas.create_function() == { 'data'  : 'could not find provided s3 bucket and s3 key',
                                                   'name'  : 'tmp_lambda_dev_test'                         ,
                                                   'status': 'error'                                       }

    def test_create_function(self):
        role_arn   = IAM_Role(lambda_name + '__tmp_role').create_for_lambda().get('role_arn')
        tmp_folder = Temp_Folder_Code()
        (
                self.lambdas.set_role       (role_arn         )
                            .set_s3_bucket  (tmp_s3_bucket    )
                            .set_s3_key     (tmp_s3_key       )
                            .set_folder_code(tmp_folder.folder)
                            .set_trace_mode ('PassThrough'    )                                                 # remove default XRays enable setting (since it requires more privs)
        )
        assert self.lambdas.create_params() == (  lambda_name, 'python3.6'         ,
                                                  role_arn   , lambda_name + '.run',
                                                  3008       , 60                  ,
                                                  {'Mode': 'PassThrough'},
                                                  { 'S3Bucket': tmp_s3_bucket,'S3Key'   : tmp_s3_key})          # confirm values that will be passed to the boto3's create_function


        assert self.lambdas.upload() is True

        result = self.lambdas.create_function()
        data   = result.get('data')
        name   = result.get('name')
        status = result.get('status')

        assert status == 'ok'
        assert name   == lambda_name

        expected_arn = 'arn:aws:lambda:{0}:{1}:function:{2}'.format(region,account_id,lambda_name)

        (Assert(data).field_is_equal('CodeSize'     , 212                    )
                     .field_is_equal('FunctionArn'  , expected_arn           )
                     .field_is_equal('FunctionName' , lambda_name            )
                     .field_is_equal('Handler'      , lambda_name + '.run'   )
                     .field_is_equal('MemorySize'   , 3008                   )
                     .field_is_equal('Role'         , role_arn               )
                     .field_is_equal('Runtime'      , 'python3.6'            )
                     .field_is_equal('Timeout'      , 60                     )
                     .field_is_equal('TracingConfig', {'Mode': 'PassThrough'})
                     .field_is_equal('Version'      , '$LATEST'              )
        )


        assert self.lambdas.delete() is True                                                                 # confirm Lambda was deleted


    def test_upload(self):
        tmp_folder = Temp_Folder_Code()

        (self.lambdas.set_s3_bucket  (tmp_s3_bucket        )
                     .set_s3_key     (tmp_s3_key           )
                     .set_folder_code(tmp_folder.folder   ))

        self.lambdas.upload()
        assert tmp_folder.s3_file_exists() is True

        downloaded_file = self.lambdas.s3().file_download(tmp_s3_bucket,tmp_s3_key)     # download file uploaded
        assert Files.exists(downloaded_file)
        unzip_location = tmp_folder.folder + '_unzipped'
        Files.unzip_file(downloaded_file,unzip_location)                                # unzip it
        assert Files.contents(Files.find(unzip_location+'/*').pop()) == lambda_code     # confirm unzipped file's contents

        tmp_folder.delete_s3_file()


    # def test_constructor(self):
    #     assert self.test_lambda.role      == 'arn:aws:iam::244560807427:role/lambda_with_s3_access'
    #     assert self.test_lambda.s3_bucket == 'gs-lambda-tests'
    #     assert self.test_lambda.name      == self.name
    #     assert self.test_lambda.handler   == self.handler
    #     assert self.test_lambda.s3_key    == 'dinis/lambdas/{0}.zip'.format(self.name)
    #
    #     assert os.path.exists(self.test_lambda.source) is True



    # def test_upload_update(self):
    #     assert self.test_lambda.delete() == self.test_lambda
    #     assert self.test_lambda.exists() is False
    #     assert self.test_lambda.update() == self.test_lambda               # first update will  update s3 bucket and create function
    #     assert self.test_lambda.invoke() == "hello None"
    #     assert self.test_lambda.update() == self.test_lambda               # 2nd update will just update s3 bucket and call the update function method
    #     assert self.test_lambda.invoke() == "hello None"
    #     assert self.test_lambda.delete() == self.test_lambda

class Temp_Folder_Code:
    def __init__(self):
        self.s3 = S3()
        self.folder = Files.temp_folder('tmp_lambda_')
        self.create_temp_file()

    def create_temp_file(self):

        tmp_file = Files.path_combine(self.folder, '{0}.py'.format(lambda_name))
        Files.write(tmp_file, lambda_code)
        assert Files.exists(tmp_file)
        #assert self.s3_file_exists() is False
        return self

    def s3_file_exists(self):
        return self.s3.file_exists(tmp_s3_bucket, tmp_s3_key)

    def delete_s3_file(self):
        self.s3.file_delete(tmp_s3_bucket, tmp_s3_key)
        assert self.s3_file_exists() is False
        return self