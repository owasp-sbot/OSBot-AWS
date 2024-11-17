from osbot_aws.AWS_Config                        import aws_config
from osbot_aws.aws.s3.S3__DB_Base                import S3__DB_Base, S3_DB_BASE__BUCKET_NAME__PREFIX, S3_DB_BASE__SERVER_NAME, S3_DB_BASE__BUCKET_NAME__SUFFIX
from osbot_aws.testing.TestCase__S3__Temp_Bucket import TestCase__S3__Temp_Bucket


class test_TestCase__S3__Temp_S3_Bucket(TestCase__S3__Temp_Bucket):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        assert cls.s3_db_base.bucket_exists()    is False

    def test__setUpClass(self):

        assert type(self.s3_db_base)               is S3__DB_Base
        assert self.s3_db_base.using_local_stack() is True
        assert self.s3_db_base.bucket_exists()     is True
        #assert aws_config.account_id()           == self.random_aws_creds.env_vars['AWS_ACCOUNT_ID']
        assert self.s3_db_base.s3_bucket()         == f'{S3_DB_BASE__BUCKET_NAME__PREFIX}-{aws_config.account_id()}-{S3_DB_BASE__BUCKET_NAME__SUFFIX}'
        assert self.s3_db_base.server_name         == S3_DB_BASE__SERVER_NAME


