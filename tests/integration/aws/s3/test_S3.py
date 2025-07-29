import os
from unittest                                                 import TestCase
from osbot_aws.AWS_Config                                     import aws_config
from osbot_aws.aws.s3.S3                                      import S3
from osbot_utils.helpers.duration.decorators.capture_duration import capture_duration
from osbot_utils.testing.Temp_File                            import Temp_File
from osbot_utils.utils.Misc                                   import random_text
from tests.integration.osbot_aws__objs_for__integration_tests import setup__osbot_aws__integration_tests


TEST__AWS_ACCOUNT_ID              = '000011110000'
LOCAL_STACK__BUCKET_NAME__POSTFIX = '.s3.localhost.localstack.cloud:4566/'

class Test_S3(TestCase):


    @classmethod
    def setUpClass(cls):
        #cls.local_stack = Local_Stack().activate()
        #assert cls.local_stack.is_local_stack_configured_and_available() is True
        setup__osbot_aws__integration_tests()
        cls.s3 = S3()
        assert cls.s3.client().meta.endpoint_url == 'http://localhost:4566'
        cls.temp_file_name       = "aaa.txt"  # todo: fix test that is leaving this file in the file system
        cls.temp_file_contents   = "some contents"
        cls.test_bucket          = "osbot-temp-bucket"
        cls.test_folder          = "unit_tests"
        cls.test_region          = aws_config.region_name() or  'eu-west-1'       # todo: figure out why other regions like 'eu-west-2' trigger an localstack's "IllegalLocationConstraintException error (when calling the CreateBucket operation: The unspecified location constraint is incompatible for the region specific endpoint this request was sent to)",
        cls.test_s3_key          = f"{cls.test_folder}/{cls.temp_file_name}"
        cls.versioning           = True
        if cls.s3.bucket_not_exists(cls.test_bucket):
            create_bucket_result = cls.s3.bucket_create(cls.test_bucket, cls.test_region, versioning=cls.versioning)
            assert create_bucket_result.get('status') == 'ok'
        assert cls.s3.file_create_from_string(file_contents=cls.temp_file_contents, bucket=cls.test_bucket, key=cls.test_s3_key) is True


    @classmethod
    def tearDownClass(cls):
        assert cls.s3.file_delete  (bucket=cls.test_bucket, key=cls.test_s3_key) is True

        assert cls.s3.bucket_delete_all_files(cls.test_bucket                  ) is True
        assert cls.s3.bucket_delete(cls.test_bucket                            ) is True
        assert cls.s3.file_exists  (bucket=cls.test_bucket, key=cls.test_s3_key) is False
        # assert cls.local_stack.is_local_stack_configured_and_available() is True
        # cls.local_stack.deactivate()                                      # for now deactivate # todo remove other classes dependency on Minio
        # assert cls.local_stack.is_local_stack_configured_and_available() is False
        #super().tearDownClass()

    def test__ctor__(self):
        assert self.s3.__class__.__name__ == 'S3'

    def test_bucket_create_delete(self):
        bucket_name = random_text('temp_bucket').lower().replace('_','-')
        assert self.s3.bucket_exists(bucket_name                  ) is False
        assert self.s3.bucket_create(bucket_name, self.test_region) == { 'status':'ok', 'data':f'/{bucket_name}'}
        assert self.s3.bucket_exists(bucket_name                  ) is True
        assert self.s3.bucket_delete(bucket_name                  ) is True
        assert self.s3.bucket_exists(bucket_name                  ) is False

    def test_bucket_exists(self):
        bucket_name = random_text('temp_bucket').lower().replace('_', '-')
        with capture_duration() as duration_1:
            assert self.s3.bucket_exists(bucket_name) is False

        with capture_duration() as duration_2:
            assert S3().bucket_exists(bucket_name) is False

        assert duration_1.seconds < 0.01  # reusing object should take less than 20ms           (it is usually about 0.004)
        assert duration_2.seconds < 0.04  # craeting new object should take less than 40ms      (it is usually about 0.013)




    def test_bucket_notification(self):
        assert self.s3.bucket_notification(self.test_bucket) == {}      # todo: add test when bucket_notification returns values

    def test_bucket_notification_create(self):                          # todo: add test that uses a temp lambda so that we can test the full workflow
        bucket_name = self.test_bucket
        lambda_arn  = 'arn:aws:lambda:eu-west-1:311800962295:function:gw_bot_lambdas_aws_on_s3_event'
        events      = ['s3:ObjectCreated:*']
        prefix      = ''

        notification_config = {'LambdaFunctionConfigurations': [{
                                'LambdaFunctionArn': lambda_arn,
                                'Events'           : events,
                                'Filter'           : { 'Key': { 'FilterRules': [ {'Name' : 'prefix',
                                                                                  'Value': prefix }]}}}]}
        result = self.s3.bucket_notification_create(bucket_name, notification_config)
        assert result == {'error': 'An error occurred (InvalidArgument) when calling the '
                                   'PutBucketNotificationConfiguration operation: Unable to validate '
                                    'the following destination configurations'}

        # todo: add test that implements the full event raise workflow below
        # 'LambdaFunctionConfigurations': [ { 'Events': ['s3:ObjectCreated:*'],
        #                                      'Id': '7db8de74-0b1f-483e-a56e-5f866844953b',
        #'LambdaFunctionArn': 'arn:aws:lambda:eu-west-1:311800962295:function:gw_bot_lambdas_aws_on_s3_event'}],


        # resource = s3.s3_bucket_notification(bucket_name)
        # config = { 'LambdaFunctionConfigurations': [{ 'LambdaFunctionArn': lambda_arn           ,
        #                                               'Events'           : ['s3:ObjectCreated:*']}]}
        # Dev.pprint(config)
        # Dev.pprint(resource.put(NotificationConfiguration=config))

        # Dev.pprint(resource.lambda_function_configurations)

        # Dev.pprint(s3.s3().get_bucket_notification_configuration(Bucket=bucket_name))

        # bucket_notification = s3.BucketNotification('bucket_name')
        # Dev.pprint(bucket_notification)

        # s3.boto_client_s3().bucket_notification()

    def test_buckets(self):
        names = self.s3.buckets()
        assert self.test_bucket in names

    #@unittest.skip("find better search target")
    def test_find_files    (self):
        prefix       = self.test_folder
        find_filter  = 'aaa'
        files        = self.s3.find_files(self.test_bucket, prefix, find_filter)
        assert files == ['unit_tests/aaa.txt']
        assert len(files) > 0


    def test_file_contents_delete_exists_upload   (self):
        file_contents = random_text(length=100)
        with Temp_File(contents=file_contents) as temp_file:
            file_path     = temp_file.file_path
            s3_bucket     = self.test_bucket
            s3_key        = os.path.join(self.test_folder, temp_file.file_name())

            assert temp_file.contents()                                           == file_contents    # confirm local file contents
            assert self.s3.file_exists(s3_bucket, s3_key                        ) is False            # confirm file doesn't exist (in s3)

            assert self.s3.file_upload(file_path, s3_bucket, self.test_folder) == s3_key              # upload file (create it in s3)

            assert self.s3.file_exists(s3_bucket, s3_key                        ) is True             # confirm file exists (in s3)
            assert self.s3.file_contents(s3_bucket, s3_key                      ) == file_contents    # confirm file contents are expected
            file_details = self.s3.file_details(s3_bucket, s3_key )
            assert file_details== { 'AcceptRanges'        : 'bytes'                         ,
                                   'ContentLength'        : 105                             ,
                                   'ContentType'          : 'binary/octet-stream'           ,
                                   'ETag'                 : file_details.get('ETag')        ,
                                   'LastModified'         : file_details.get('LastModified'),
                                   'Metadata'             : {}                              ,
                                    'ServerSideEncryption': 'AES256'                        ,
                                    'VersionId'           : file_details.get('VersionId')   }         # this exists because we have versioning enabled in this test bucket


            assert self.s3.file_delete(s3_bucket, s3_key                        ) is True             # delete file
            assert self.s3.file_exists(s3_bucket, s3_key                        ) is False            # confirm file doesn't exist (in s3)


    def test_file_create_from_string(self):
        file_contents = 'some test'
        bucket        = self.test_bucket                                                        # target bucket
        key           = os.path.join(self.test_folder, 'some-temp-file.txt')                    # key is folder + file

        assert self.s3.file_exists            (bucket, key               ) is False             # confirm file doesn't exist in s3
        assert self.s3.file_create_from_string(file_contents, bucket, key) is True              # create file in s3 (from string)
        assert self.s3.file_exists            (bucket, key               ) is True              # confirm file exists
        assert self.s3.file_contents          (bucket, key               ) == file_contents     # confirm file contents match
        assert self.s3.file_delete            (bucket, key               ) is True              # delete file

    def test_file_move(self):
        file_contents = 'some test'

        src_bucket  = self.test_bucket
        src_key     = self.test_folder + '/src_file.txt'
        dest_bucket = self.test_bucket
        dest_key    = self.test_folder + '/dest_file.txt'

        assert self.s3.file_create_from_string(file_contents, src_bucket, src_key              ) is True

        assert self.s3.file_exists            (src_bucket   , src_key                          ) is True
        assert self.s3.file_exists            (dest_bucket  , dest_key                         ) is False

        assert self.s3.file_move              (src_bucket   , src_key   , dest_bucket, dest_key) is True

        assert self.s3.file_exists            (src_bucket   , src_key                          ) is False
        assert self.s3.file_exists            (dest_bucket  , dest_key                         ) is True

        assert self.s3.file_contents          (dest_bucket  , dest_key                         ) == file_contents
        assert self.s3.file_delete            (src_bucket   , src_key                          ) is True
        assert self.s3.file_delete            (dest_bucket  , dest_key                         ) is True

    def test_policy(self):
        bucket_policy = self.s3.policy(self.test_bucket)
        #self.result = self.s3.policy_create('gw-bot-trails',bucket_policy)
        assert bucket_policy == {'Statement': []}                               # todo: add test that create and check a bucket policy

    def test_policy_statements(self):
        assert self.s3.policy_statements(self.test_bucket) == []                # todo: add test that create and check policy_statements
        # assert len(self.s3.policy_statements('gw-tf-cloud-trails', index_by='Effect').get('Allow')) == 4
        # assert len(self.s3.policy_statements('gw-tf-cloud-trails', group_by='Effect').get('Allow')) == 2

    def test_policy_statements__new(self):
        s3_bucket    = self.test_bucket
        action       = 'action'
        effect       = 'effect'
        service      = 'service'
        trail_name   = 'trail_name'
        account_id   = 'account_id'
        resource_arn = self.s3.policy_statements__resource_arn(s3_bucket, trail_name, account_id )
        result       = self.s3.policy_statements__new(action, effect, service, resource_arn)
        assert result == { 'Action'     : 'action'              ,
                           'Effect'     : 'effect'              ,
                           'Principal'  : {'Service': 'service' },
                           'Resource'   : 'arn:aws:s3:::osbot-temp-bucket/trail_name/AWSLogs/account_id/*'}

    def test_policy_statements__without(self):
        result = self.s3.policy_statements__without(self.test_bucket, 'Action', 's3:PutObject')
        assert result == []                             # todo: add test that create and check policy_statements


