from time import sleep

import pytest
from osbot_utils.utils import Misc
from osbot_utils.utils.Files import file_exists, file_contents, Files

from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.OSBot_Setup import OSBot_Setup
from osbot_aws.apis.IAM import IAM
from osbot_aws.apis.S3 import S3
from osbot_aws.apis.Session import Session
from osbot_aws.helpers.Test_Helper           import Test_Helper
from osbot_aws.apis.Lambda                   import Lambda
from osbot_aws.apis.test_helpers.Temp_Lambda import Temp_Folder_With_Lambda_File, Temp_Lambda
from osbot_aws.apis.test_helpers.Temp_Queue  import Temp_Queue
from osbot_aws.helpers.IAM_Role              import IAM_Role
from osbot_utils.utils.Assert import Assert


class test_Lambda(Test_Helper):

    @staticmethod
    def setup_test_enviroment():            # todo: refactor into separate class

        Test_Helper().check_aws_token()

        s3                = S3()
        setup             = OSBot_Setup()
        s3_bucket_lambdas = setup.s3_bucket_lambdas
        s3_region         = setup.region_name

        if s3.bucket_not_exists(s3_bucket_lambdas):
            s3.bucket_create(s3_bucket_lambdas, s3_region)
            print('>>>> Created bucket', s3_bucket_lambdas)


    @classmethod
    def setUpClass(cls) -> None:
        cls.setup_test_enviroment()


    #@aws_inject('region,account_id')
    def setUp(self):   # self, region, account_id):
        super().setUp()
        self.lambda_name = 'tmp_lambda_dev_test'
        self.setup       = super().setUp()
        self.s3_bucket   = self.setup.s3_bucket_lambdas
        self.region      = self.setup.region_name
        self.account_id  = self.setup.account_id
        self.s3_key      = f'{AWS_Config().lambda_s3_key_prefix()}/{self.lambda_name}.zip' #'lambdas/{0}.zip'.format(self.lambda_name)
        self.aws_lambda  = Lambda(self.lambda_name)


    def test__init__(self):
        assert self.aws_lambda.runtime == 'python3.8'
        assert self.aws_lambda.memory == 3008
        assert self.aws_lambda.timeout == 60
        assert self.aws_lambda.original_name == self.lambda_name
        assert self.aws_lambda.s3().bucket_exists(self.s3_bucket)

    def test_account_settings(self):
        assert self.aws_lambda.account_settings().get('AccountLimit').get('CodeSizeUnzipped') == 262144000

    def test_aliases(self):
        lambda_api = self.aws_lambda                                        # make it easier to read below
        alias_name        = 'temp_name'
        alias_description = 'temp description'
        function_version  = '$LATEST'
        with Temp_Lambda() as temp_lambda:
            assert lambda_api.aliases     (function_name    = temp_lambda.arn()      ) == []
            assert lambda_api.alias_create(function_name    = temp_lambda.lambda_name,
                                           function_version = function_version       ,
                                           name             = alias_name             ,
                                           description      = alias_description      ).get('Name') == alias_name
            data = lambda_api.alias       (function_name    = temp_lambda.lambda_name,
                                           name             = alias_name             )
            del data['RevisionId']
            assert data == { 'AliasArn'      : f'{temp_lambda.arn()}:{alias_name}',
                            'Description'    : alias_description                  ,
                            'FunctionVersion': function_version                   ,
                            'Name'           : alias_name                         }

            assert lambda_api.aliases(function_name= temp_lambda.arn(),index_by='Name').get(alias_name).get('Description') == alias_description
            assert lambda_api.alias_delete(temp_lambda.lambda_name, alias_name) == {}
            assert lambda_api.aliases(function_name=temp_lambda.arn())          == []

    def test_create_function__no_params(self):
        assert self.aws_lambda.create() == {'error': "missing fields in create_function: ['role', 's3_bucket', 's3_key']"}

    def test_create_function(self):
        role_arn   = IAM_Role(self.lambda_name + '__tmp_role').create_for__lambda().get('role_arn')
        tmp_folder = Temp_Folder_With_Lambda_File(self.lambda_name).create_temp_file()
        (
                self.aws_lambda.set_role         (role_arn)
                                 .set_s3_bucket  (self.s3_bucket    )
                                 .set_s3_key     (self.s3_key       )
                                 .set_folder_code(tmp_folder.folder)
        )

        assert self.aws_lambda.create_params() == (self.lambda_name, 'python3.8'              ,     # confirm values that will be passed to the boto3's create_function
                                                   role_arn        , self.lambda_name + '.run',
                                                   3008            , 60                       ,
                                                   { 'Mode'    : 'PassThrough'               },
                                                   { 'S3Bucket': self.s3_bucket               ,
                                                     'S3Key'   : self.s3_key                 },
                                                   None, None)

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
                     .field_is_equal('Runtime'      , 'python3.8'              )
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

    def test_configuration(self):
        with Temp_Lambda() as temp_lambda:
            aws_lambda = temp_lambda.aws_lambda
            value = 10
            assert aws_lambda.configuration() == aws_lambda.info().get('Configuration')
            assert aws_lambda.configuration_update(Timeout=value).get('Timeout') == value
            assert aws_lambda.configuration().get('Timeout') == value

    def test_event_sources(self):
        assert type(self.aws_lambda.event_sources()) == list                    # todo: add test with actual event_sources
        #self.result = self.aws_lambda.event_sources()


    def test_event_source_create(self):
        with Temp_Lambda() as temp_lambda:                                      # create a temp lambda function that will deleted on exit
            with Temp_Queue() as temp_queue:                                    # create a temp sqs queue that will be deleted on exit
                event_source_arn = temp_queue .queue.arn()
                lambda_name      = temp_lambda.lambda_name
                aws_lambda       = temp_lambda.aws_lambda
                queue            = temp_queue .queue

                aws_lambda.configuration_update(Timeout=10)                     # needs to be less than 30 (which is the default value sent in the queue)
                queue.policy_add_sqs_permissions_to_lambda_role(lambda_name)    # add permissions needed to role
                sleep(2)                                                        # todo: need a better solution to find out when the permission is available
                aws_lambda.event_source_create(event_source_arn, lambda_name)   # todo: add asserts
                queue.policy_remove_sqs_permissions_to_lambda_role(lambda_name) # remove permissions todo: create custom role

    def test_event_source_delete(self):
        for uuid in self.aws_lambda.event_sources(index_by='UUID'):
            self.result = self.aws_lambda.event_source_delete(uuid)     # these take a bit of time to delete

    def test_invoke_raw(self):
        with Temp_Lambda() as temp_lambda:
            result   = temp_lambda.aws_lambda.invoke_raw({'name' : temp_lambda.lambda_name})
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
            result = temp_lambda.aws_lambda.invoke({'name': temp_lambda.lambda_name})
            assert result == 'hello {0}'.format(temp_lambda.lambda_name)

    def test_invoke_async(self):
        with Temp_Lambda() as temp_lambda:
            result = temp_lambda.aws_lambda.invoke_async({'name': temp_lambda.lambda_name})
            assert result.get('StatusCode') == 202

    def test_functions(self):
        functions = list(self.aws_lambda.functions())
        if len(functions) == 0:
            pytest.skip("There where no Lambda functions in the target AWS region ")
        assert len(functions) > 0
        assert set(functions.pop(0)) == {'CodeSha256', 'CodeSize'     , 'Description'  , 'FunctionArn', 'FunctionName',
                                           'Handler'   , 'LastModified' , 'MemorySize'   , 'RevisionId' , 'Role'        ,
                                           'Runtime'   , 'Timeout'      , 'TracingConfig', 'Version'                    }


    def test_policy__permissions(self):
        with Temp_Lambda() as temp_lambda:
            temp_lambda.aws_lambda.permission_add(temp_lambda.arn(), 'an_id', 'lambda:action', 'lambda.amazonaws.com')
            if len(temp_lambda.aws_lambda.permissions()) == 0:
                pytest.skip("in test_policy__permissions, len(temp_lambda.aws_lambda.permissions()) was 0 (doesn't happen when executing it directly")  # todo: fix this race condition that happens when running all tests at the same time
            assert temp_lambda.aws_lambda.permissions()[0].get('Action') == 'lambda:action'

    def test_update(self):
        with Temp_Lambda() as temp_lambda:
            tmp_text = Misc.random_string_and_numbers(prefix='updated code ')
            temp_lambda.tmp_folder.create_temp_file('def run(event, context): return "{0}"'.format(tmp_text))
            temp_lambda.aws_lambda.set_folder_code(temp_lambda.tmp_folder.folder )
            result = temp_lambda.aws_lambda.update()
            status = result.get('status')
            data   = result.get('data')


            assert 'TracingConfig' in data['update_code'] #set(data) == { 'CodeSha256', 'CodeSize', 'Description', 'FunctionArn', 'FunctionName', 'Handler', 'LastModified', 'MemorySize', 'ResponseMetadata', 'RevisionId', 'Role', 'Runtime', 'Timeout', 'TracingConfig', 'Version'}
            assert status    == 'ok'
            assert temp_lambda.aws_lambda.invoke() == tmp_text

    def test_upload(self):
        tmp_folder = Temp_Folder_With_Lambda_File(self.lambda_name).create_temp_file()

        (self.aws_lambda.set_s3_bucket   (self.s3_bucket       )
                        .set_s3_key      (self.s3_key          )
                        .set_folder_code(tmp_folder.folder   ))

        #self.aws_lambda.upload()
        #assert tmp_folder.s3_file_exists() is True

        downloaded_file = self.aws_lambda.s3().file_download(self.s3_bucket, self.s3_key)             # download file uploaded
        assert file_exists(downloaded_file) is True
        unzip_location = tmp_folder.folder + '_unzipped'
        Files.unzip_file(downloaded_file,unzip_location)                                        # unzip it
        assert file_contents(Files.find(unzip_location+'/*').pop()) == tmp_folder.lambda_code  # confirm unzipped file's contents

        self.aws_lambda.s3().file_delete(self.s3_bucket, self.s3_key)


    # def test_upload_update(self):
    #     assert self.test_lambda.delete() == self.test_lambda
    #     assert self.test_lambda.exists() is False
    #     assert self.test_lambda.update() == self.test_lambda               # first update will  update s3 bucket and create function
    #     assert self.test_lambda.invoke() == "hello None"
    #     assert self.test_lambda.update() == self.test_lambda               # 2nd update will just update s3 bucket and call the update function method
    #     assert self.test_lambda.invoke() == "hello None"
    #     assert self.test_lambda.delete() == self.test_lambda


