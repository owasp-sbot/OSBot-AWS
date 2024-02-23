from functools import cache
from unittest import TestCase

from dotenv import load_dotenv

from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.aws.dynamo_db.Dynamo_DB import Dynamo_DB
from osbot_aws.aws.dynamo_db.Dynamo_DB__Table import Dynamo_DB__Table
from osbot_aws.aws.iam.IAM_Assume_Role import IAM_Assume_Role
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set, is_guid
from tests.integration.aws.dynamo_db.TestCase__Temp_Dynamo_DB_Table import TestCase__Temp_Dynamo_DB_Table
from tests.integration.aws.dynamo_db.test_Dynamo_DB import Dynamo_DB__with_temp_role

TEST_TABLE_NAME = 'temp_table__test_Dynamo_DB__Table'

class test_Dynamo_DB__Table(TestCase__Temp_Dynamo_DB_Table):

    @classmethod
    def setUpClass(cls):
        cls.table_name     = TEST_TABLE_NAME
        cls.remove_on_exit = False
        super().setUpClass()

    def test__init__(self):
        assert self.table.table_name == TEST_TABLE_NAME

    def test_add_document(self):
        with self.table as _:
            result = _.add_document({'answer': 42})
            status = result.get('status')
            data   = result.get('data')
            assert list_set(result) == ['data', 'status']
            assert list_set(data  ) == ['document', 'document_as_item', 'key_value']
            assert status == 'ok'
            document         = data.get('document')
            document_as_item = data.get('document_as_item')
            document_key     = data.get('key_value')
            assert is_guid(document_key) is True
            assert document_key        == document_as_item.get('el-key').get('S')
            assert document            == {'answer':42, 'el-key': document_key}
            assert document_as_item    == {'answer': {'N': '42'}, 'el-key': {'S': document_key}}

            assert _.delete_document(document_key) == {'data': True, 'status': 'ok'}

    def test_clear_table(self):
        with self.table as _:
            assert _.clear_table() == {'data': {'delete_result': [], 'deleted_keys': [],'delete_status': True}, 'status': 'ok'}
            document_key = _.add_document({}).get('data').get('key_value')
            assert _.clear_table() == {'data'  : {'delete_result': [{'UnprocessedItems': {}}],
                                                  'deleted_keys' : [document_key]           ,
                                                  'delete_status': True                     },
                                       'status': 'ok'}

    def test_exists(self):
        assert self.table.exists() == {'data': True, 'status': 'ok'}

    def test_info(self):
        aws_config  = AWS_Config()
        account_id  = aws_config.account_id()
        region_name = aws_config.region_name()
        result      =  self.table.info()
        data        = result.get('data'  )
        status      = result.get('status')
        table_id    = data.get('TableId')
        del data['CreationDateTime']
        del data['BillingModeSummary']['LastUpdateToPayPerRequestDateTime']

        assert list_set(result)  == ['data', 'status']
        assert list_set(data)    == ['AttributeDefinitions', 'BillingModeSummary', 'DeletionProtectionEnabled', 'ItemCount', 'KeySchema', 'ProvisionedThroughput', 'TableArn', 'TableId', 'TableName', 'TableSizeBytes', 'TableStatus']
        assert is_guid(table_id) is True

        assert data == {  'AttributeDefinitions'     : [{'AttributeName': self.key_name, 'AttributeType': 'S'}]              ,
                           'BillingModeSummary'      : {'BillingMode': 'PAY_PER_REQUEST'},

                          'DeletionProtectionEnabled': False                                                                 ,
                          'ItemCount'                : 0                                                                     ,
                          'KeySchema'                : [{'AttributeName': self.key_name, 'KeyType': 'HASH'}]                 ,
                          'ProvisionedThroughput'    : { 'NumberOfDecreasesToday': 0 ,
                                                         'ReadCapacityUnits'     : 0 ,
                                                         'WriteCapacityUnits'    : 0 }                                       ,
                          'TableArn'                 : f'arn:aws:dynamodb:{region_name}:{account_id}:table/{self.table_name}',
                          'TableId'                  : table_id                                                              ,
                          'TableName'                : self.table_name                                                       ,
                          'TableSizeBytes'           : 0                                                                     ,
                          'TableStatus'              : 'ACTIVE'                                                              }

    def test_status(self):
        assert self.table.status() == {'data': 'ACTIVE', 'status': 'ok'}
