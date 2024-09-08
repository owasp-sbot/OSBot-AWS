from unittest import TestCase

from osbot_aws.aws.dynamo_db.Dynamo_DB__Table import Dynamo_DB__Table
from osbot_aws.aws.dynamo_db.Dynamo_DB__with_temp_role import Dynamo_DB__with_temp_role
from osbot_aws.testing.Pytest import skip_pytest___aws_pytest_user_name__is_not_set
from osbot_aws.testing.TestCase__Dynamo_DB__Local import TestCase__Dynamo_DB__Local, URL_DOCKER__DYNAMODB__LOCAL
from osbot_utils.utils.Dev import pprint


class TestCase__Temp_Dynamo_DB_Table(TestCase__Dynamo_DB__Local):

    table          : Dynamo_DB__Table   = None
    key_name       : str                = 'el-key'
    table_name     : str                = 'temp_table__TestCase__Temp_Dynamo_DB_Table'
    #remove_on_exit : bool             = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.table           = Dynamo_DB__Table(table_name=cls.table_name, key_name=cls.key_name)
        cls.table.create_table()
        assert cls.dynamo_db.client().meta.endpoint_url == URL_DOCKER__DYNAMODB__LOCAL
        assert cls.table_name in cls.dynamo_db.tables()

    @classmethod
    def tearDownClass(cls):
        #if cls.remove_on_exit:
        cls.table.delete_table()
        super().tearDownClass()