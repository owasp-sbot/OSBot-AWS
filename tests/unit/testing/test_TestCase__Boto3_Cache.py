from botocore.client                            import BaseClient
from osbot_aws.testing.TestCase__Boto3_Cache    import TestCase__Boto3_Cache

class test_TestCase__Boto3_Cache(TestCase__Boto3_Cache):
    original__make_api_call__qualname__ = 'BaseClient._make_api_call'
    patched__make_api_call__qualname__  = 'Sqlite__Cache__Requests__Patch.patch_apply.<locals>.proxy'

    @classmethod
    def setUpClass(cls):
        assert BaseClient._make_api_call.__qualname__ == cls.original__make_api_call__qualname__
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        assert BaseClient._make_api_call.__qualname__ == cls.patched__make_api_call__qualname__
        super().tearDownClass()
        assert BaseClient._make_api_call.__qualname__ == cls.original__make_api_call__qualname__

    def test_setUpClass(self):
        assert BaseClient._make_api_call.__qualname__ == self.patched__make_api_call__qualname__

