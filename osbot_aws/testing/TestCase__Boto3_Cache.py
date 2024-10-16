from unittest                                   import TestCase
from botocore.client                            import BaseClient
from osbot_utils.utils.Env                      import load_dotenv
from osbot_aws.aws.boto3.Cache_Boto3_Requests   import Cache_Boto3_Requests
from osbot_aws.testing.Pytest                   import skip_pytest___aws_pytest_user_name__is_not_set


class TestCase__Boto3_Cache(TestCase):
    cache : Cache_Boto3_Requests

    @classmethod
    def setUpClass(cls):
        skip_pytest___aws_pytest_user_name__is_not_set()
        load_dotenv()
        cls.cache = Cache_Boto3_Requests()
        cls.cache.patch_apply()

    @classmethod
    def tearDownClass(cls):
        cls.cache.patch_restore()
        assert BaseClient._make_api_call.__qualname__ == 'BaseClient._make_api_call'  # confirm the original function is still there
