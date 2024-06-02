from os import environ

from botocore.client                                            import BaseClient
from osbot_aws.aws.boto3.Cache_Boto3_Requests                   import Cache_Boto3_Requests, SQLITE_DB_NAME__BOTO3_REQUESTS_CACHE, SQLITE_TABLE_NAME__BOTO3_REQUESTS
from osbot_aws.testing.TestCase__Boto3_Cache                    import TestCase__Boto3_Cache
from osbot_utils.base_classes.Kwargs_To_Self                    import Kwargs_To_Self
from osbot_utils.helpers.sqlite.Sqlite__Database                import Sqlite__Database
from osbot_utils.helpers.sqlite.domains.Sqlite__DB__Local       import Sqlite__DB__Local, ENV_NAME_PATH_LOCAL_DBS
from osbot_utils.helpers.sqlite.cache.db.Sqlite__DB__Requests   import Sqlite__DB__Requests
from osbot_utils.utils.Files                                    import parent_folder
from osbot_utils.utils.Objects                                  import base_types


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

        assert type(self.cache) == Cache_Boto3_Requests

        with self.cache.sqlite_requests as _:
            assert type(_)       == Sqlite__DB__Requests
            assert base_types(_) == [Sqlite__DB__Local, Sqlite__Database, Kwargs_To_Self, object]
            local_dbs = environ.get(ENV_NAME_PATH_LOCAL_DBS)
            if local_dbs:
                assert parent_folder(_.db_path)      == local_dbs
                assert _.db_name                     == SQLITE_DB_NAME__BOTO3_REQUESTS_CACHE
                assert _.table_requests().table_name == SQLITE_TABLE_NAME__BOTO3_REQUESTS
                assert _.tables_names()              == [ SQLITE_TABLE_NAME__BOTO3_REQUESTS                       ,
                                                         f'idx__{SQLITE_TABLE_NAME__BOTO3_REQUESTS}__request_hash']


