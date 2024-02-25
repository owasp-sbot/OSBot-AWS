from unittest import TestCase

from osbot_aws.aws.dynamo_db.Dynamo_DB__Table import Dynamo_DB__Table
from tests.integration.aws.dynamo_db.test_Dynamo_DB import Dynamo_DB__with_temp_role


class TestCase__Temp_Dynamo_DB_Table(TestCase):

    table          : Dynamo_DB__Table
    key_name       : str = 'el-key'
    table_name     : str = 'temp_table__TestCase__Temp_Dynamo_DB_Table'
    remove_on_exit : bool = False

    @classmethod
    def setUpClass(cls):
        cls.table           = Dynamo_DB__Table(table_name=cls.table_name, key_name=cls.key_name)
        cls.table.dynamo_db = Dynamo_DB__with_temp_role()
        cls.table.create_table()

    @classmethod
    def tearDownClass(cls):
        if cls.remove_on_exit:
            cls.table.delete_table()