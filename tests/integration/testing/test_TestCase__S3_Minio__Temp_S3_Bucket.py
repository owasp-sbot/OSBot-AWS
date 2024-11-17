from osbot_aws.AWS_Config                                       import aws_config
from osbot_aws.aws.s3.S3__DB_Base                               import S3__DB_Base, S3_DB_BASE__BUCKET_NAME__PREFIX, S3_DB_BASE__SERVER_NAME, S3_DB_BASE__BUCKET_NAME__SUFFIX
from osbot_aws.testing.TestCase__S3_Minio__Temp_S3_Bucket       import TestCase__S3_Minio__Temp_S3_Bucket
from osbot_utils.utils.Env                                      import in_github_action
from osbot_utils.utils.Misc                                     import list_set


class test_TestCase__S3_Minio__Temp_S3_Bucket(TestCase__S3_Minio__Temp_S3_Bucket):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        assert cls.s3_db_base.bucket_exists()    is False

    def test__setUpClass(self):
        if in_github_action():
            assert list_set(self.extra_env_vars)             == [ 'AWS_ACCESS_KEY_ID'           ,
                                                                  'AWS_ACCOUNT_ID'              ,
                                                                  'AWS_DEFAULT_REGION'          ,
                                                                  'AWS_SECRET_ACCESS_KEY'       ,
                                                                  'USE_MINIO_AS_S3'             ]
            assert self.random_aws_creds.original_env_vars   == { 'AWS_ACCESS_KEY_ID'    : None ,
                                                                  'AWS_ACCOUNT_ID'       : None ,
                                                                  'AWS_DEFAULT_REGION'   : 'eu-west-1', # todo: figure out why this is happening (this could be the cause of the IllegalLocationConstraintException bug we saw in test_S3
                                                                  'AWS_SECRET_ACCESS_KEY': None ,
                                                                  'USE_MINIO_AS_S3'      : None }
        assert type(self.s3_db_base)             is S3__DB_Base
        assert self.s3_db_base.bucket_exists()   is True
        assert aws_config.account_id()           == self.random_aws_creds.env_vars['AWS_ACCOUNT_ID']
        assert self.s3_db_base.s3_bucket()       == f'{S3_DB_BASE__BUCKET_NAME__PREFIX}-{aws_config.account_id()}-{S3_DB_BASE__BUCKET_NAME__SUFFIX}'
        assert self.s3_db_base.use_minio         is True
        assert self.s3_db_base.server_name       == S3_DB_BASE__SERVER_NAME


