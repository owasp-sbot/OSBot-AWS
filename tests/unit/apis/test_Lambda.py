import unittest


from pbx_gs_python_utils.utils.Assert        import Assert
from pbx_gs_python_utils.utils.Files         import Files
from pbx_gs_python_utils.utils.Misc          import Misc
from osbot_aws.apis.IAM                      import IAM
from osbot_aws.Globals                       import Globals
from gw_bot.helpers.Test_Helper              import Test_Helper
from osbot_aws.apis.Lambda                   import Lambda
from osbot_aws.apis.test_helpers.Temp_Lambda import Temp_Folder_Code, Temp_Lambda
from osbot_aws.helpers.IAM_Role              import IAM_Role

class test_Lambda(Test_Helper):

    def setUp(self):
        super().setUp()
        self.iam         = IAM()
        self.region      = self.iam.region()
        self.account_id  = self.iam.account_id()
        self.lambda_name = 'tmp_lambda_dev_test'
        self.setup       = super().setUp()
        self.s3_bucket   = self.setup.s3_bucket_lambdas
        self.s3_key      = f'{Globals.lambda_s3_key_prefix}/{self.lambda_name}.zip' #'lambdas/{0}.zip'.format(self.lambda_name)
        self.aws_lambda  = Lambda(self.lambda_name)

    def test__init__(self):
        assert self.aws_lambda.runtime == 'python3.7'
        assert self.aws_lambda.memory == 3008
        assert self.aws_lambda.timeout == 60
        assert self.aws_lambda.original_name == self.lambda_name
        assert self.aws_lambda.s3().bucket_exists(self.s3_bucket)

    def test_create_function__no_params(self):
        assert self.aws_lambda.create() == {'error': "missing fields in create_function: ['role', 's3_bucket', 's3_key']"}

    def test_create_function(self):
        role_arn   = IAM_Role(self.lambda_name + '__tmp_role').create_for__lambda().get('role_arn')
        tmp_folder = Temp_Folder_Code(self.lambda_name)
        (
                self.aws_lambda.set_role         (role_arn)
                                 .set_s3_bucket  (self.s3_bucket    )
                                 .set_s3_key     (self.s3_key       )
                                 .set_folder_code(tmp_folder.folder)
        )

        assert self.aws_lambda.create_params() == (self.lambda_name, 'python3.7'              ,
                                                   role_arn        , self.lambda_name + '.run',
                                                   3008            , 60                       ,
                                                   { 'Mode'    : 'PassThrough'               },
                                                   { 'S3Bucket': self.s3_bucket               ,
                                                     'S3Key'   : self.s3_key                 })  # confirm values that will be passed to the boto3's create_function

        assert self.aws_lambda.upload() is True

        result = self.aws_lambda.create()
        data   = result.get('data')
        name   = result.get('name')
        status = result.get('status')

        assert status == 'ok'
        assert name   == self.lambda_name

        expected_arn = 'arn:aws:lambda:{0}:{1}:function:{2}'.format(self.region,self.account_id,self.lambda_name)              # expected arn value

        (Assert(data).field_is_equal('CodeSize'     , 209                      )                                  # confirm lambda creation details
                     .field_is_equal('FunctionArn'  , expected_arn             )
                     .field_is_equal('FunctionName' , self.lambda_name         )
                     .field_is_equal('Handler'      , self.lambda_name + '.run')
                     .field_is_equal('MemorySize'   , 3008                     )
                     .field_is_equal('Role'         , role_arn                 )
                     .field_is_equal('Runtime'      , 'python3.7'              )
                     .field_is_equal('Timeout'      , 60                       )
                     .field_is_equal('TracingConfig', {'Mode': 'PassThrough'}  )
                     .field_is_equal('Version'      , '$LATEST'                )
        )


        assert self.aws_lambda.delete() is True     # confirm Lambda was deleted

    def test_create_function__bad_s3_key_(self):
        self.aws_lambda.set_role('').set_s3_bucket('').set_s3_key('')
        assert self.aws_lambda.create() == { 'data'  : 'could not find provided s3 bucket and s3 key',
                                             'name'  : 'tmp_lambda_dev_test'                         ,
                                             'status': 'error'                                       }

    def test_invoke_raw(self):
        with Temp_Lambda() as temp_lambda:
            result   = temp_lambda.temp_lambda.invoke_raw({'name' : temp_lambda.lambda_name})
            data     = result.get('data')
            name     = result.get('name')
            status   = result.get('status')
            response = result.get('response')
            assert status == 'ok'
            assert name   == temp_lambda.lambda_name
            assert data   == 'hello {0}'.format(temp_lambda.lambda_name)
            assert response.get('StatusCode') == 200

    def test_invoke(self):
        with Temp_Lambda() as temp_lambda:
            result = temp_lambda.temp_lambda.invoke({'name': temp_lambda.lambda_name})
            assert result == 'hello {0}'.format(temp_lambda.lambda_name)

    def test_invoke_async(self):
        with Temp_Lambda() as temp_lambda:
            result = temp_lambda.temp_lambda.invoke_async({'name': temp_lambda.name})
            assert result.get('StatusCode') == 202

    def test_functions(self):
        functions = list(self.aws_lambda.functions())
        #function = functions.get(self.lambda_name)
        assert len(functions) > 0
        assert set(functions.pop(0)) == {'CodeSha256', 'CodeSize'     , 'Description'  , 'FunctionArn', 'FunctionName',
                                           'Handler'   , 'LastModified' , 'MemorySize'   , 'RevisionId' , 'Role'        ,
                                           'Runtime'   , 'Timeout'      , 'TracingConfig', 'Version'                    }




    def test_update(self):
        with Temp_Lambda() as temp_lambda:
            tmp_text = Misc.random_string_and_numbers(prefix='updated code ')
            temp_lambda.tmp_folder.create_temp_file('def run(event, context): return "{0}"'.format(tmp_text))

            result = temp_lambda.temp_lambda.update()
            status = result.get('status')
            data   = result.get('data')

            assert set(data) == { 'CodeSha256', 'CodeSize', 'Description', 'FunctionArn', 'FunctionName', 'Handler', 'LastModified', 'MemorySize', 'ResponseMetadata', 'RevisionId', 'Role', 'Runtime', 'Timeout', 'TracingConfig', 'Version'}
            assert status    == 'ok'
            assert temp_lambda.temp_lambda.invoke() == tmp_text

    def test_upload(self):
        tmp_folder = Temp_Folder_Code(self.lambda_name)

        (self.aws_lambda.set_s3_bucket   (self.s3_bucket       )
                         .set_s3_key     (self.s3_key          )
                         .set_folder_code(tmp_folder.folder   ))

        self.aws_lambda.upload()
        assert tmp_folder.s3_file_exists() is True

        downloaded_file = self.aws_lambda.s3().file_download(self.s3_bucket, self.s3_key)             # download file uploaded
        assert Files.exists(downloaded_file)
        unzip_location = tmp_folder.folder + '_unzipped'
        Files.unzip_file(downloaded_file,unzip_location)                                        # unzip it
        assert Files.contents(Files.find(unzip_location+'/*').pop()) == tmp_folder.lambda_code  # confirm unzipped file's contents

        tmp_folder.delete_s3_file()


    # def test_upload_update(self):
    #     assert self.test_lambda.delete() == self.test_lambda
    #     assert self.test_lambda.exists() is False
    #     assert self.test_lambda.update() == self.test_lambda               # first update will  update s3 bucket and create function
    #     assert self.test_lambda.invoke() == "hello None"
    #     assert self.test_lambda.update() == self.test_lambda               # 2nd update will just update s3 bucket and call the update function method
    #     assert self.test_lambda.invoke() == "hello None"
    #     assert self.test_lambda.delete() == self.test_lambda


