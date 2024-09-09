from osbot_aws.aws.s3.S3                import S3
from osbot_aws.testing.TestCase__Minio  import TestCase__Minio, TEST__AWS_DEFAULT_REGION, TEST__AWS_ACCOUNT_ID
from osbot_utils.utils.Env              import get_env
from osbot_utils.utils.Functions        import function_name


class test_TestCase__Minio(TestCase__Minio):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        assert function_name(getattr(S3, 'client')) == 'client'

    def test__setUpClass(self):
        assert self.aws_account_id            == get_env('AWS_ACCOUNT_ID'    , TEST__AWS_ACCOUNT_ID    )
        assert self.aws_default_region        == get_env('AWS_DEFAULT_REGION', TEST__AWS_DEFAULT_REGION)

        assert self.hook_method.target_module                 == S3
        assert self.hook_method.target_method                 == 'client'
        assert self.hook_method.wrapper_method                == getattr(S3, 'client')
        assert function_name(self.hook_method.target)         == 'client'
        assert function_name(self.hook_method.wrapper_method) == 'wrapper_method'
        assert function_name(getattr(S3, 'client')          ) == 'wrapper_method'
        #assert self.hook_method.target        == getattr(S3, 'client')

