from unittest import TestCase

from osbot_aws.aws.dynamo_db.Dynamo_DB__Record import Dynamo_DB__Record
from osbot_aws.aws.dynamo_db.Dynamo_DB__Table import Dynamo_DB__Table
from tests.integration.aws.dynamo_db.TestCase__Temp_Dynamo_DB_Table import TestCase__Temp_Dynamo_DB_Table
from tests.integration.aws.dynamo_db.test_Dynamo_DB import Dynamo_DB__with_temp_role

TEST_TABLE_NAME = 'temp_table__test_Dynamo_DB__Record'

class test_Dynamo_DB__Record(TestCase__Temp_Dynamo_DB_Table):

    @classmethod
    def setUpClass(cls):
        cls.remove_on_exit = False
        cls.table_name     = TEST_TABLE_NAME
        super().setUpClass()

    def setUp(self):
        self.db_record = Dynamo_DB__Record()

    def test__init__(self):
        assert self.table.table_name == TEST_TABLE_NAME
        expected_locals = {'data': {}, 'data_binary': b'', 'metadata': {}}
        assert self.db_record.__locals__() == expected_locals

    def test_table(self):
        assert self.table.exists() is True

