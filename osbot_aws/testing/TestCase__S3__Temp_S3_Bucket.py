from unittest                                           import TestCase
from osbot_local_stack.local_stack.Local_Stack          import Local_Stack
from osbot_aws.aws.s3.S3__DB_Base                       import ENV_NAME__USE_MINIO_AS_S3, S3__DB_Base
from osbot_aws.testing.Temp__Random__AWS_Credentials    import Temp__Random__AWS_Credentials
from osbot_utils.utils.Env                              import get_env


class TestCase__S3__Temp_S3_Bucket(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.local_stack = Local_Stack().activate()
        cls.random_aws_creds  = Temp__Random__AWS_Credentials().set_vars()
        cls.s3_db_base        = S3__DB_Base()
        with cls.s3_db_base as _:
            assert _.using_local_stack() is True
            _.setup()                                           # this will create the temp bucket
            assert _.bucket_exists() is True

    @classmethod
    def tearDownClass(cls):
        with cls.s3_db_base as _:
            assert _.using_local_stack      () is True
            assert _.bucket_delete_all_files() is True
            assert _.bucket_delete          () is True
        cls.random_aws_creds.restore_vars()

        cls.local_stack.deactivate()