from decimal import Decimal
import pytest
from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.aws.boto3.View_Boto3_Rest_Calls import print_boto3_calls
from osbot_aws.aws.dynamo_db.Dynamo_DB__Table import Dynamo_DB__Table
from osbot_aws.aws.dynamo_db.domains.DyDB__Table import DyDB__Table
from osbot_aws.aws.dynamo_db.domains.DyDB__Timeseries import DyDB__Timeseries, NAME_TIMESTAMP
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import timestamp_utc_now, random_int, list_set, is_int, is_guid, wait_for
from osbot_aws.testing.TestCase__Dynamo_DB import TestCase__Dynamo_DB
from osbot_utils.utils.Objects import base_types


#@pytest.mark.skip()
# todo: figure out why it takes so long to run the setUpClass and __init__() methods
class test_DyDB__Timeseries(TestCase__Dynamo_DB):
    dydb_timeseries : DyDB__Timeseries
    delete_on_exit  : bool             = False
    partition       : str              = 'OSBOT_TEST'
    table_name      : str              = 'pytest_db_timestamp'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dydb_timeseries           = DyDB__Timeseries(table_name=cls.table_name)
        cls.dydb_timeseries.dynamo_db = cls.dynamo_db
        #if cls.dydb_timeseries.not_exists():
        #assert cls.dydb_timeseries.create_table() is True

    @classmethod
    def tearDownClass(cls):
        if cls.delete_on_exit:
            assert cls.dydb_timeseries.delete_table(wait_for_deletion=False)  == {'data': True, 'status': 'ok'}


    def test__init__(self):
        aws_config = AWS_Config()
        assert aws_config.region_name() == 'eu-west-1'
        expected_var = { 'dynamo_db'                : self.dynamo_db    ,
                         'global_secondary_indexes' : []                ,
                         'index_name'               : 'timestamp_index' ,
                         'index_type'               : 'RANGE'           ,
                         'key_name'                 : 'id'              ,
                         'key_type'                 : 'S'           ,
                         'table_name'               : self.table_name   }
        with self.dydb_timeseries as _:
            assert _.__locals__() == expected_var
            assert base_types(_) == [DyDB__Table, Dynamo_DB__Table, Kwargs_To_Self, object]


    def test_exists(self):
        assert self.dydb_timeseries.exists() is False


    def test_create_kwargs(self):
        with self.dydb_timeseries  as _:
            default_kwargs = { 'AttributeDefinitions': [ { 'AttributeName'         : _.key_name    , 'AttributeType': _.key_type},
                                                         { 'AttributeName'         : NAME_TIMESTAMP, 'AttributeType': 'N'}],
                                                           'BillingMode'           :  'PAY_PER_REQUEST',
                                                           'GlobalSecondaryIndexes': [ { 'IndexName': _.index_name,
                                                                                         'KeySchema': [ { 'AttributeName': NAME_TIMESTAMP, 'KeyType': 'HASH'},
                                                                                                        { 'AttributeName': _.key_name    , 'KeyType': 'RANGE'}],
                                                                                         'Projection': {'ProjectionType': 'ALL'}}],
                                                           'KeySchema'              : [{'AttributeName': _.key_name, 'KeyType': 'HASH'}],
                                                           'TableName'              : _.table_name}
            assert self.dydb_timeseries.create_kwargs() == default_kwargs
    # def test_all_ids(self):
    #     pprint(self.dydb_timeseries.all_ids())

    # def test__clear_table(self):
    #     result = self.dydb_timeseries.clear_table()
    #     #pprint(result)

    def test_add_gsi(self):
        with self.dydb_timeseries as _:
            # create_kwargs =  {
            #     'IndexName': 'string',
            #     'KeySchema': [ { 'AttributeName': 'string', 'KeyType': 'HASH' },],
            #     'Projection': { 'ProjectionType': 'ALL',                   }}
            result        = _.gsi_create(index_name='string')
            pprint(result)

            #pprint(_.info())

    def test_delete_gsi(self):
        with self.dydb_timeseries as _:
            result = _.gsi_delete(index_name='string')
            pprint(result)

    def test_create_table(self):
        with self.dydb_timeseries as _:
            if _.not_exists():
                print('creating table')
                assert _.create_table() is True
            table_info = _.info()
            LastUpdateToPayPerRequestDateTime = table_info.get('BillingModeSummary').get('LastUpdateToPayPerRequestDateTime')
            CreationDateTime                  = table_info.get('CreationDateTime'  )
            TableId                           = table_info.get('TableId'           )
            assert table_info == { 'AttributeDefinitions': [ {'AttributeName': _.key_name, 'AttributeType': _.key_type},
                                                             { 'AttributeName': 'timestamp',
                                                               'AttributeType': 'N'}],
                                   'BillingModeSummary': { 'BillingMode': 'PAY_PER_REQUEST',
                                                           'LastUpdateToPayPerRequestDateTime': LastUpdateToPayPerRequestDateTime},
                                   'CreationDateTime': CreationDateTime,
                                   'DeletionProtectionEnabled': False,
                                   'GlobalSecondaryIndexes': [ { 'IndexArn': 'arn:aws:dynamodb:eu-west-1:470426667096:table/pytest_db_timestamp/index/timestamp_index',
                                                                 'IndexName': 'timestamp_index',
                                                                 'IndexSizeBytes': 0,
                                                                 'IndexStatus': 'ACTIVE',
                                                                 'ItemCount': 0,
                                                                 'KeySchema': [ { 'AttributeName': 'timestamp',
                                                                                  'KeyType': 'HASH'},
                                                                                { 'AttributeName': 'id',
                                                                                  'KeyType': 'RANGE'}],
                                                                 'Projection': {'ProjectionType': 'ALL'},
                                                                 'ProvisionedThroughput': { 'NumberOfDecreasesToday': 0,
                                                                                            'ReadCapacityUnits': 0,
                                                                                            'WriteCapacityUnits': 0}}],
                                   'ItemCount': 0,
                                   'KeySchema': [{'AttributeName': 'id', 'KeyType': 'HASH'}],
                                   'ProvisionedThroughput': { 'NumberOfDecreasesToday': 0,
                                                              'ReadCapacityUnits': 0,
                                                              'WriteCapacityUnits': 0},
                                   'TableArn': 'arn:aws:dynamodb:eu-west-1:470426667096:table/pytest_db_timestamp',
                                   'TableId': TableId,
                                   'TableName': 'pytest_db_timestamp',
                                   'TableSizeBytes': 0,
                                   'TableStatus': 'ACTIVE'}

    #@pytest.mark.skip("needs to be fixed")  # todo don't use documents() which will fetch all items (use smaller query)
    def test_add_document(self):
        documents_before = self.dydb_timeseries.documents(partition=self.partition)

        #pprint(documents_before)

        value            = Decimal(random_int())
        data             = dict(answer= value, another_key='123', and_another='456')
        data_serialised  = self.dynamo_db.document_serialise(data)
        result           = self.dydb_timeseries.add_document(data, partition=self.partition)

        status            = result     .get('status'          )
        result_data       = result     .get('data'            )
        document          = result_data.get('document'        )
        document_as_item  = result_data.get('document_as_item')
        timestamp         = result_data.get('key_value'       )
        document_data     = document   .get('data'            )
        dy_id             = document   .get('dy_id'           )

        assert result.get('dy_id')        == dy_id
        assert document_data              == data
        assert status                     == 'ok'
        assert is_int(timestamp          ) is True
        assert is_guid(dy_id             ) is True
        assert list_set(data             ) == ['and_another', 'another_key', 'answer'                         ]
        assert list_set(result           ) == ['data'       , 'dy_id', 'status'                               ]
        assert list_set(result_data      ) == ['document'   , 'document_as_item','key_value'                  ]
        assert list_set(document         ) == ['data'       , 'dy_id'           , 'partition_key', 'timestamp']
        assert list_set(document_as_item ) == ['data'       , 'dy_id'           , 'partition_key', 'timestamp']
        assert data_serialised             ==  { 'and_another': {'S': '456'     },
                                                 'another_key': {'S': '123'     },
                                                 'answer'     : {'N': str(value)}}

        assert result_data ==  { 'document'        : { 'data'         : data                    ,
                                                       'dy_id'        : dy_id                   ,
                                                       'partition_key': self.partition          ,
                                                       'timestamp'    : timestamp               },
                                 'document_as_item': { 'data'         : { 'M': data_serialised  },
                                                       'dy_id'        : { 'S': dy_id            },
                                                       'partition_key': {'S': self.partition    },
                                                       'timestamp'    : {'N': str(timestamp)    }},
                                  'key_value'      : timestamp }

        documents_after = self.dydb_timeseries.documents(partition=self.partition)
        for i in range(1,10):
            if len(documents_after) != len(documents_before) + 1:               # if we didn't get a result
                pprint("document not avaiable yet, so waiting for 1 second")
                wait_for(1)                                                     # wait for 1 sec (sometimes this is needed)
                documents_after = self.dydb_timeseries.documents(partition=self.partition)
                #pprint(documents_after)
            else:
                break
        assert len(documents_before) == len(documents_after) - 1

        for doc in documents_after:
            assert list_set(doc)             == ['data', 'dy_id', 'partition_key', 'timestamp']

            #pprint(doc)
            #assert list_set(doc.get('data')) == ['and_another', 'another_key', 'answer']
            #assert doc.get('data').get('another_key') == '123'
            #assert doc.get('data').get('and_another') == '456'

    def test_query_by_partition(self):
        items           = self.dydb_timeseries.query_by_partition(self.partition)
        assert len(items) > 0


    def test_query_by_last_n_hours(self):
        hours = 0.2
        items = self.dydb_timeseries.query_by_last_n_hours(hours, partition=self.partition)
        assert len(items) > 0
        #pprint(items)

    def test_query_by_timestamp(self):
        hours = 1
        start_timestamp = timestamp_utc_now() - (hours * 60 * 60 * 1000)            # get logs from last hour
        end_timestamp   = timestamp_utc_now()

        items = self.dydb_timeseries.query_by_timestamp(start_timestamp=start_timestamp, end_timestamp=end_timestamp, partition=self.partition)

        assert len(items) > 0
        # for index, item in enumerate(items):
        #     timestamp = item.get('timestamp')
        #     data      = item.get('data'     )
        #     #assert list(data) == ['answer', 'another_key', 'and_another']
        #     when = timestamp_to_datetime(timestamp)
        #     #print(index, timestamp,when,  data)

    # def test_info(self):
    #     result = self.dydb_timeseries.info().get('data')
    #     pprint(result)

    @pytest.mark.skip(reason="FIX test to have valid data") # todo: fix test
    def test_query_by_env_and_var(self):
        query_var   = 'ip_address'
        query_value = '35.205.163.48'  # Google's IP Address
        env         = None
        items       = self.dydb_timeseries.query_by_env_and_var(query_var, query_value, env)
        assert len(items) > 0
