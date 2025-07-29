import datetime

import pytest
from dateutil.tz                                                    import tzlocal
from osbot_utils.utils.Misc                                         import list_set, is_guid
from tests.integration.aws.dynamo_db.TestCase__Temp_Dynamo_DB_Table import TestCase__Temp_Dynamo_DB_Table


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
            assert list_set(data  ) == ['document', 'document_as_item']
            assert status == 'ok'
            document         = data.get('document')
            document_as_item = data.get('document_as_item')
            document_key     = document.get(self.key_name)
            assert is_guid(document_key) is True
            assert document_key        == document_as_item.get('el-key').get('S')
            assert document            == {'answer':42, 'el-key': document_key}
            assert document_as_item    == {'answer': {'N': '42'}, 'el-key': {'S': document_key}}

            assert _.delete_document(document_key) == {'data': True, 'status': 'ok'}

    #@pytest.mark.skip('to: fix test that started to fail after some refactoring')
    def test_clear_table(self):
        with self.table as _:
            clear_result = _.clear_table()
            assert list_set(clear_result            ) == ['data', 'status']
            assert list_set(clear_result.get('data')) == ['delete_result', 'delete_status','deleted_keys']
            document_key = _.add_document({}).get('data').get('document').get('el-key')
            assert _.clear_table() == {'data'  : {'delete_result': [{'UnprocessedItems': {}}],
                                                  'deleted_keys' : [document_key]           ,
                                                  'delete_status': True                     },
                                       'status': 'ok'}

    def test_exists(self):
        assert self.table.exists() == {'data': True, 'status': 'ok'}

    def test_info(self):
        account_id  = self.aws_config.account_id()
        region_name = self.aws_config.region_name()
        result      =  self.table.info()
        data        = result.get('data'  )
        table_id    = data.get('TableId')
        del data['CreationDateTime']
        del data['BillingModeSummary']['LastUpdateToPayPerRequestDateTime']

        assert list_set(result)  == ['data', 'status']
        assert list_set(data)    == ['AttributeDefinitions', 'BillingModeSummary', 'DeletionProtectionEnabled', 'ItemCount', 'KeySchema',
                                     'ProvisionedThroughput', 'Replicas', 'TableArn', 'TableId', 'TableName', 'TableSizeBytes', 'TableStatus']
        assert is_guid(table_id) is True

        assert data == {  'AttributeDefinitions'     : [{'AttributeName': self.key_name, 'AttributeType': 'S'}]              ,
                           'BillingModeSummary'      : {'BillingMode': 'PAY_PER_REQUEST'},

                          'DeletionProtectionEnabled': False                                                                 ,
                          'ItemCount'                : data.get('ItemCount')                                                                     ,
                          'KeySchema'                : [{'AttributeName': self.key_name, 'KeyType': 'HASH'}]                 ,
                          'ProvisionedThroughput'    : { 'LastDecreaseDateTime': datetime.datetime(1970, 1, 1, 0, 0, tzinfo=tzlocal()),         # only in minio
                                                         'LastIncreaseDateTime': datetime.datetime(1970, 1, 1, 0, 0, tzinfo=tzlocal()),         # only in minio
                                                         'NumberOfDecreasesToday': 0 ,
                                                         'ReadCapacityUnits'     : 0 ,
                                                         'WriteCapacityUnits'    : 0 }                                       ,
                          'Replicas'                 : [],
                          'TableArn'                 : f'arn:aws:dynamodb:{region_name}:{account_id}:table/{self.table_name}',
                          'TableId'                  : table_id                                                              ,
                          'TableName'                : self.table_name                                                       ,
                          'TableSizeBytes'           : data.get('TableSizeBytes')                                                                     ,
                          'TableStatus'              : 'ACTIVE'                                                              }

    def test_status(self):
        assert self.table.status() == {'data': 'ACTIVE', 'status': 'ok'}