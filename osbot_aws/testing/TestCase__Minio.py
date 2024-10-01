from osbot_aws.aws.s3.S3                import S3
from osbot_aws.aws.s3.S3__Minio         import S3__Minio
from osbot_utils.testing.Temp_Env_Vars  import Temp_Env_Vars
from unittest                           import TestCase
from osbot_utils.testing.Hook_Method    import Hook_Method
from osbot_utils.utils.Env              import get_env

TEST__AWS_ACCOUNT_ID     = '000011110000'
TEST__AWS_DEFAULT_REGION = 'eu-west-1'


class TestCase__Minio(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.aws_account_id     = get_env('AWS_ACCOUNT_ID'    , TEST__AWS_ACCOUNT_ID    )        # use existing values if they already exist
        cls.aws_default_region = get_env('AWS_DEFAULT_REGION', TEST__AWS_DEFAULT_REGION)
        tmp_vars_values        = dict(AWS_ACCOUNT_ID     = cls.aws_account_id    ,
                                      AWS_DEFAULT_REGION = cls.aws_default_region)
        cls.tmp_env_vars       = Temp_Env_Vars(env_vars=tmp_vars_values).set_vars()
        cls.hook_method        = Hook_Method(S3, 'client'      )       # todo: see if we also need to hook the main S3 class (from osbot_aws)
        cls.hook_method.mock_call = cls.s3_minio__s3_client
        cls.hook_method.wrap()

    @classmethod
    def tearDownClass(cls):
        cls.hook_method.unwrap()
        cls.tmp_env_vars.restore_vars()

    def s3_minio__s3_client(self):
        return S3__Minio().s3_client()