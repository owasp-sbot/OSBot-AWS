from unittest                                           import TestCase
from osbot_aws.aws.s3.S3__DB_Base                       import ENV_NAME__USE_MINIO_AS_S3, S3__DB_Base
from osbot_aws.testing.Temp__Random__AWS_Credentials    import Temp__Random__AWS_Credentials
from osbot_utils.utils.Env                              import get_env


class TestCase__S3_Minio__Temp_S3_Bucket(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.extra_env_vars   = { ENV_NAME__USE_MINIO_AS_S3: 'True'}
        cls.random_aws_creds  = Temp__Random__AWS_Credentials(env_vars=cls.extra_env_vars).set_vars()
        cls.s3_db_base        = S3__DB_Base(use_minio=True)
        assert get_env(ENV_NAME__USE_MINIO_AS_S3) == 'True'  # confirm value has been set
        with cls.s3_db_base as _:
            assert _.using_minio() is True                      # confirm we are using Minio
            _.setup()                                           # this will create the temp bucket
            assert _.bucket_exists() is True

    @classmethod
    def tearDownClass(cls):
        with cls.s3_db_base as _:
            assert _.using_minio            () is True
            assert _.bucket_delete_all_files() is True
            assert _.bucket_delete          () is True
        cls.random_aws_creds.restore_vars()