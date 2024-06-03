from unittest import TestCase

from osbot_aws.aws.dynamo_db.Dynamo_DB__Table import Dynamo_DB__Table
from osbot_aws.aws.dynamo_db.Dynamo_DB__with_temp_role import Dynamo_DB__with_temp_role
from osbot_aws.testing.Pytest import skip_pytest___aws_pytest_user_name__is_not_set


class TestCase__Temp_Dynamo_DB_Table(TestCase):

    table          : Dynamo_DB__Table
    key_name       : str = 'el-key'
    table_name     : str = 'temp_table__TestCase__Temp_Dynamo_DB_Table'
    remove_on_exit : bool = True

    @classmethod
    def setUpClass(cls):
        skip_pytest___aws_pytest_user_name__is_not_set()
        cls.table           = Dynamo_DB__Table(table_name=cls.table_name, key_name=cls.key_name)
        cls.table.dynamo_db = Dynamo_DB__with_temp_role()
        cls.table.create_table()

    @classmethod
    def tearDownClass(cls):
        if cls.remove_on_exit:
            cls.table.delete_table()