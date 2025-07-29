from osbot_aws.testing.TestCase__Dynamo_DB__Local import TestCase__Dynamo_DB__Local
from osbot_utils.utils.Misc                       import list_set
from osbot_utils.utils.Objects                    import type_full_name


#class test_Dynamo_DB(TestCase__Boto3_Cache):
class test_Dynamo_DB(TestCase__Dynamo_DB__Local):           # todo: see if these tests still make sense: we are not testing the TestCase__Boto3_Cache, because we are using TestCase__Dynamo_DB__Local
    table_name      : str
    table_key       : str

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.table_name = 'temp-table'
        cls.table_key = 'an_key'
        cls.dynamo_db.table_create(table_name=cls.table_name, key_name=cls.table_key)        # usually takes about 5 seconds to create

    @classmethod
    def tearDownClass(cls) -> None:
        assert cls.dynamo_db.table_delete(table_name=cls.table_name, wait_for_deletion=True) is True
        super().tearDownClass()

    def test_client(self):
        assert type_full_name(self.dynamo_db.client()) == 'botocore.client.DynamoDB'

    def test_documents_all(self):
        assert self.dynamo_db.documents_all(table_name=self.table_name) == []

    def test_dynamo_streams(self):
        assert type_full_name(self.dynamo_db.client__dynamo_streams()) == 'botocore.client.DynamoDBStreams'

    def test_table_exists(self):
        assert self.dynamo_db.table_exists(table_name=self.table_name) is True

    def test_table_info(self):
        assert self.dynamo_db.table_info(table_name='AAAA-Not-Exists') == {}
        table_info = self.dynamo_db.table_info(table_name=self.table_name)
        assert list_set(table_info) == ['AttributeDefinitions', 'BillingModeSummary', 'CreationDateTime', 'DeletionProtectionEnabled',
                                        'ItemCount', 'KeySchema', 'ProvisionedThroughput', 'Replicas', 'TableArn', 'TableId',
                                        'TableName', 'TableSizeBytes', 'TableStatus']

    def test_table_status(self):
        assert self.dynamo_db.table_status(table_name=self.table_name) == 'ACTIVE'

    def test_tables(self):
        tables = self.dynamo_db.tables()
        assert type(tables)     == list
        assert self.table_name  in tables

