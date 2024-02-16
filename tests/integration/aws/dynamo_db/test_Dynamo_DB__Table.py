from functools import cache
from unittest import TestCase

from dotenv import load_dotenv

from osbot_aws.aws.dynamo_db.Dynamo_DB import Dynamo_DB
from osbot_aws.aws.dynamo_db.Dynamo_DB__Table import Dynamo_DB__Table
from osbot_aws.aws.iam.IAM_Assume_Role import IAM_Assume_Role
from osbot_utils.utils.Misc import list_set
from tests.integration.aws.dynamo_db.test_Dynamo_DB import Dynamo_DB__with_temp_role


class test_Dynamo_DB__Table(TestCase):
    table          : Dynamo_DB__Table
    key_name       : str = 'el-key'
    table_name     : str = 'temp_table__test_Dynamo_DB__Table'
    remove_on_exit : bool = True

    @classmethod
    def setUpClass(cls):
        cls.table           = Dynamo_DB__Table(table_name=cls.table_name, key_name=cls.key_name)
        cls.table.dynamo_db = Dynamo_DB__with_temp_role()
        cls.table.create()

    @classmethod
    def tearDownClass(cls):
        if cls.remove_on_exit:
            cls.table.delete()

    def test_exists(self):
        assert self.table.exists() is True

    def test_info(self):
        assert list_set(self.table.info()) == ['AttributeDefinitions', 'CreationDateTime', 'DeletionProtectionEnabled', 'ItemCount', 'KeySchema', 'ProvisionedThroughput', 'TableArn', 'TableId', 'TableName', 'TableSizeBytes', 'TableStatus']