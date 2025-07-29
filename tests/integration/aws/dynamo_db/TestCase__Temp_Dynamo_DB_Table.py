from osbot_aws.apis.Session import URL__LOCAL_STACK__ENDPOINT_URL
from osbot_aws.aws.dynamo_db.Dynamo_DB__Table       import Dynamo_DB__Table
from osbot_aws.testing.TestCase__Dynamo_DB__Local   import TestCase__Dynamo_DB__Local


class TestCase__Temp_Dynamo_DB_Table(TestCase__Dynamo_DB__Local):

    table          : Dynamo_DB__Table   = None
    key_name       : str                = 'el-key'
    table_name     : str                = 'temp_table__TestCase__Temp_Dynamo_DB_Table'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.table           = Dynamo_DB__Table(table_name=cls.table_name, key_name=cls.key_name)
        cls.table.create_table()
        assert cls.dynamo_db.client().meta.endpoint_url == URL__LOCAL_STACK__ENDPOINT_URL
        assert cls.table_name in cls.dynamo_db.tables()

    @classmethod
    def tearDownClass(cls):
        cls.table.delete_table()
        super().tearDownClass()