import datetime
from decimal import Decimal

from dateutil.tz import tzlocal

from osbot_aws.AWS_Config                           import AWS_Config
from osbot_aws.aws.dynamo_db.Dynamo_DB__Table       import Dynamo_DB__Table
from osbot_aws.aws.dynamo_db.domains.DyDB__Table    import DyDB__Table
from osbot_aws.testing.TestCase__Dynamo_DB          import TestCase__Dynamo_DB
from osbot_aws.testing.TestCase__Dynamo_DB__Local import TestCase__Dynamo_DB__Local
from osbot_utils.base_classes.Kwargs_To_Self        import Kwargs_To_Self
from osbot_utils.utils.Env                          import in_github_action
from osbot_utils.utils.Lists                        import list_index_by
from osbot_utils.utils.Misc                         import random_int, list_set, is_guid
from osbot_utils.utils.Objects                      import base_types


class test_DyDB__Table(TestCase__Dynamo_DB__Local):
    delete_on_exit: bool        = True
    aws_config    : AWS_Config
    dydb_table    : DyDB__Table
    table_name    : str         = f'pytest__dydb__table__auto_delete_{delete_on_exit}'
    account_id    : str
    region_name   : str

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dydb_table   = DyDB__Table(table_name=cls.table_name, dynamo_db=cls.dynamo_db)      # set dynamo_db to version of dynamo_db from TestCase__Dynamo_DB (which has the correct IAM permissions)
        cls.aws_config   = AWS_Config()
        cls.region_name  = "ddblocal"           # (minio) cls.aws_config.region_name()
        cls.account_id   = "000000000000"       # (minio) cls.aws_config.account_id()

        cls.dydb_table.create_table()  # create if it doesn't exist

    @classmethod
    def tearDownClass(cls):
        assert cls.dydb_table.delete_table(wait_for_deletion=True) is True
        super().tearDownClass()


    def test__init__(self):
        #assert self.region_name == 'eu-west-1'
        expected_var = { 'dynamo_db'                : self.dynamo_db    ,
                         'key_name'                 : 'id'              ,
                         'key_type'                 : 'S'           ,
                         'table_name'               : self.table_name   }
        with self.dydb_table as _:
            assert _.__locals__() == expected_var
            assert base_types(_) == [Dynamo_DB__Table, Kwargs_To_Self, object]


    def test_add_document(self):
        with self.dydb_table as _:
            value            = Decimal(random_int())
            document_to_add  = dict(answer= value, another_key='123', and_another='456')
            result           = _.add_document(document_to_add)
            document_added   = result.get('document'        )
            document_as_item = result.get('document_as_item')
            document_id      = document_added.get('id')
            expected_item    = { 'and_another': {'S': '456'      },
                                 'another_key': {'S': '123'      },
                                 'answer'     : {'N': str(value) },
                                 'id'         : {'S': document_id}}
            assert list_set(result           ) == ['document'   , 'document_as_item']
            assert list_set(document_to_add  ) == ['and_another', 'another_key', 'answer'      ]
            assert list_set(document_added   ) == ['and_another', 'another_key', 'answer', 'id']
            assert list_set(document_as_item ) == ['and_another', 'another_key', 'answer', 'id']
            assert is_guid(document_id       ) is True
            assert document_as_item            == expected_item


            assert _.document       (document_id) == document_added
            assert _.document_exists(document_id) is True
            assert _.delete_document(document_id) is True
            assert _.document_exists(document_id) is False
            assert _.document       (document_id) == {}

    def test_add_documents(self):
        size             = 25
        documents_to_add = []
        for i in range(0,size)         :
            document_to_add = dict(random=Decimal(random_int()), answer=42, an_dict={'goes': 'here'})
            documents_to_add.append(document_to_add)
        with self.dydb_table as _:
            result    = _.add_documents(documents_to_add)
            documents = result.get('documents')
            responses = result.get('responses')
            assert list_set(result) == ['documents', 'responses']
            #assert responses        == [{'UnprocessedItems': {}}]
            assert len(documents)   == len(documents_to_add)
            for document in documents:
                assert list_set(document) == ['an_dict', 'answer', 'id', 'random']
            docs_by_id = list_index_by(documents, 'id')

            # with Duration(prefix='get doc one by one:'):
            #     for document_id, document in docs_by_id.items():
            #         assert _.document(document_id) == document


            documents_ids        =  list(docs_by_id.keys())
            results              = _.documents(documents_ids)
            # all_responses        = results.get('all_responses'       )
            # all_unprocessed_keys = results.get('all_unprocessed_keys')
            # assert list_set(results)    == ['all_responses', 'all_unprocessed_keys']
            # #assert all_unprocessed_keys == [{}]
            all_responses_by_id = list_index_by(results, 'id')

            assert all_responses_by_id == docs_by_id
            assert _.delete_documents(documents_ids) == [{'UnprocessedItems': {}}]
            assert _.documents(documents_ids) == []

    def test_documents_all(self):
        items = self.dydb_table.dynamo_db.documents_all(table_name=self.dydb_table.table_name, batch_size=20000, max_fetch=100001)
        for item in items:
            assert list_set(item) in [['id'] , ['an_dict', 'answer', 'id', 'random'], ['and_another', 'another_key', 'answer', 'id']]

    def test_documents_ids(self):
        documents_ids = self.dydb_table.documents_ids(batch_size=50, max_fetch=100)
        documents     = self.dydb_table.documents(documents_ids)
        assert len(documents) == len(documents_ids)


    def test_create_table(self):
        assert self.dydb_table.create_table() is False      # table was created on setUpClass so here it should fail

    def test_exists(self):
        assert self.dydb_table.exists() is True

    def test_create_table_kwargs(self):
        with self.dydb_table  as _:
            default_kwargs = { 'AttributeDefinitions': [ { 'AttributeName'         : _.key_name    , 'AttributeType': _.key_type}],
                                                           'BillingMode'           :  'PAY_PER_REQUEST',
                                                           'KeySchema'              : [{'AttributeName': _.key_name, 'KeyType': 'HASH'}],
                                                           'TableName'              : _.table_name}
            assert self.dydb_table.create_table_kwargs() == default_kwargs

    def test_info(self):
        with self.dydb_table as _:
            table_info                        = _.info()
            LastUpdateToPayPerRequestDateTime = table_info.get('BillingModeSummary').get('LastUpdateToPayPerRequestDateTime')
            CreationDateTime                  = table_info.get('CreationDateTime')
            TableId                           = table_info.get('TableId')
            assert table_info == {'AttributeDefinitions'     : [{'AttributeName': _.key_name, 'AttributeType': _.key_type}],
                                  'BillingModeSummary'       :  {'BillingMode': 'PAY_PER_REQUEST', 'LastUpdateToPayPerRequestDateTime': LastUpdateToPayPerRequestDateTime},
                                  'CreationDateTime'         : CreationDateTime ,
                                  'DeletionProtectionEnabled': False            ,
                                  'ItemCount'                : table_info.get('ItemCount')                 ,
                                  'KeySchema'                : [{'AttributeName': 'id', 'KeyType': 'HASH'}],
                                  'ProvisionedThroughput'    : { 'LastDecreaseDateTime': datetime.datetime(1970, 1, 1, 0, 0, tzinfo=tzlocal()),
                                                                 'LastIncreaseDateTime': datetime.datetime(1970, 1, 1, 0, 0, tzinfo=tzlocal()),
                                                                 'NumberOfDecreasesToday': 0               ,
                                                                 'ReadCapacityUnits': 0                    ,
                                                                 'WriteCapacityUnits': 0                   },
                                  'TableArn'                 : f'arn:aws:dynamodb:{self.region_name}:{self.account_id}:table/{self.table_name}',
                                  #'TableId'                  : TableId                                     ,
                                  'TableName'                : self.table_name                             ,
                                  'TableSizeBytes'           : table_info.get('TableSizeBytes')            ,
                                  'TableStatus'              : 'ACTIVE'                                    }

    def test_size(self):
        assert self.dydb_table.size() >= 0





    # only use when the creds expire
    # def test__temp_role__iam_reset_credentials(self):
    #     result = self.dynamo_db.temp_role__iam_reset_credentials()
    #     pprint(result)