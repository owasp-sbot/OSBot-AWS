import random
from datetime import datetime, timedelta, UTC
from decimal import Decimal

import pytest

from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.aws.dynamo_db.Dynamo_DB__Table import Dynamo_DB__Table
from osbot_aws.aws.dynamo_db.domains.DyDB__Table import DyDB__Table
from osbot_aws.aws.dynamo_db.domains.DyDB__Table_With_GSI import DyDB__Table_With_GSI
from osbot_aws.testing.TestCase__Dynamo_DB import TestCase__Dynamo_DB
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import in_github_action, random_number, timestamp_utc_now_less_delta, list_set
from osbot_utils.utils.Objects import base_types


class test_DyDB__Table(TestCase__Dynamo_DB):
    delete_on_exit     : bool                   = False            # in_github_action() #can't really do this since it takes ages (like several minutes for the GSIs to be created)
    aws_config         : AWS_Config
    dydb_table_with_gsi: DyDB__Table_With_GSI
    table_name         : str                    = f'pytest__dydb__table_with_gsi__auto_delete_{delete_on_exit}'
    account_id         : str
    region_name        : str

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dydb_table_with_gsi = DyDB__Table_With_GSI(table_name=cls.table_name, dynamo_db=cls.dynamo_db)      # set dynamo_db to version of dynamo_db from TestCase__Dynamo_DB (which has the correct IAM permissions)
        cls.aws_config          = AWS_Config()
        cls.region_name         = cls.aws_config.region_name()
        cls.account_id          = cls.aws_config.account_id()
        cls.dydb_table_with_gsi.create_table()  # create if it doesn't exist
        cls.gsi_index_name      = 'user_id'
        cls.gsi_index_type      = 'S'
        cls.gsi_sort_key        = 'timestamp'
        cls.gsi_sort_key_type   = 'N'
        cls.gsi_sort_key_schema = 'RANGE'
        cls.gsi_projection_type = 'ALL'

    @classmethod
    def tearDownClass(cls):
        if cls.delete_on_exit:
            assert cls.dydb_table_with_gsi.delete_table(wait_for_deletion=False) is True

    def test__init__(self):
        assert self.region_name == 'eu-west-1'
        expected_var = {'dynamo_db': self.dynamo_db,
                        'key_name': 'id',
                        'key_type': 'S',
                        'table_name': self.table_name}
        with self.dydb_table_with_gsi as _:
            assert _.__locals__() == expected_var
            assert base_types(_)  == [ DyDB__Table      ,
                                       Dynamo_DB__Table ,
                                       Kwargs_To_Self   ,
                                       object           ]

    def test_AAA__add_test_data(self):
        with self.dydb_table_with_gsi as _:
            if _.size() > 0:                    # there is already test data
                return
            time_groups = [0, 10, 20, 30]
            for user_id in ['user_a', 'user_b', 'user_c', 'user_d']:
                for i in range(0, 10):
                    delta_days = random.choice(time_groups)
                    timestamp = timestamp_utc_now_less_delta(days=delta_days)
                    document  = dict(user_id    = user_id                 ,
                                     an_str     = '42'                    ,
                                     an_random  = Decimal(random_number()),
                                     timestamp  = timestamp               )
                    _.add_document(document)
            pprint(f'there are {_.size()} documents')

    def test_attribute_definitions(self):
        with self.dydb_table_with_gsi as _:
            pprint(_.attribute_definitions())
            assert {'AttributeName': 'id', 'AttributeType': 'S'}  in _.attribute_definitions()


    def test_can_update_table(self):
        with self.dydb_table_with_gsi as _:
            assert _.can_update_table() is True

    def test_index_create(self):
        with self.dydb_table_with_gsi as _:
            if _.index_not_exists(self.gsi_index_name):
                create_kwargs = dict(index_name      = self.gsi_index_name      ,
                                     index_type      = self.gsi_index_type      ,
                                     sort_key        = self.gsi_sort_key        ,
                                     sort_key_type   = self.gsi_sort_key_type   ,
                                     sort_key_schema = self.gsi_sort_key_schema ,
                                     projection_type = self.gsi_projection_type )
                result = _.index_create(**create_kwargs)
                #pprint(result)

    @pytest.mark.skip("add to methods with Cache")
    def test_index_delete(self):
        with self.dydb_table_with_gsi as _:
            for index_name in _.indexes_names():
                _.index_delete(index_name=index_name)

    def test_index_exists(self):
        with self.dydb_table_with_gsi as _:
            assert _.index_exists(self.gsi_index_name) is True

    def test_index(self):
        index_name = self.gsi_index_name
        with self.dydb_table_with_gsi as _:
            index_info     = _.index(index_name)
            expected_index = { 'IndexArn'       : f'arn:aws:dynamodb:{self.region_name}:{self.account_id}:table/{self.table_name}/index/{index_name}',
                               'IndexName'      : index_name,
                               'IndexSizeBytes' : index_info.get('IndexSizeBytes')  ,
                               'IndexStatus'    : 'ACTIVE'  ,
                               'ItemCount'      : index_info.get('ItemCount'     )  ,
                               'KeySchema'      : [{'AttributeName': self.gsi_index_name, 'KeyType': 'HASH'},
                                                   {'AttributeName': self.gsi_sort_key  , 'KeyType': self.gsi_sort_key_schema}],
                               'Projection'     : {'ProjectionType': 'ALL'},
                               'ProvisionedThroughput': { 'NumberOfDecreasesToday': 0, 'ReadCapacityUnits': 0, 'WriteCapacityUnits': 0}}

            assert index_info == expected_index


    def test_indexes(self):
        with self.dydb_table_with_gsi as _:
            gs_indexes = _.indexes()
            assert gs_indexes == _.info().get('GlobalSecondaryIndexes', [])

    def test_indexes_names(self):
        with self.dydb_table_with_gsi as _:
            gs_indexes_names = _.indexes_names()
            pprint(gs_indexes_names)

    def test_table_status(self):
        with self.dydb_table_with_gsi as _:
            assert _.table_status     () == 'ACTIVE'
            assert _.indexes_status() in [['ACTIVE'], []]


    def test_query_index(self):
        user_id = 'user_a'
        with self.dydb_table_with_gsi as _:
            query_kwargs = dict(index_name    = self.gsi_index_name,
                                index_type    = self.gsi_index_type,
                                index_value   = user_id            )

            items = _.query_index(**query_kwargs)
            assert len(items) == 10
            for raw_item in items:
                item = _.dynamo_db.document_deserialise(raw_item)
                assert list_set(item) == ['an_random', 'an_str', 'id', 'timestamp', 'user_id']
                assert item.get('an_str') == '42'
                assert item.get('user_id') == user_id

    def test_query_index_between_range(self):
        user_id = 'user_b'
        timestamp_start = timestamp_utc_now_less_delta(days=21)
        timestamp_end   = timestamp_utc_now_less_delta(days=10)
        with self.dydb_table_with_gsi as _:
            query_kwargs = dict(index_name    = self.gsi_index_name,
                                index_type    = self.gsi_index_type,
                                index_value   = user_id,
                                sort_key      = self.gsi_sort_key       ,
                                sort_key_type = self.gsi_sort_key_type  ,
                                start_value   = timestamp_start         ,
                                end_value     = timestamp_end           )

            items = _.query_index_between_range(**query_kwargs)
            assert len(items) > 0
            for raw_item in items:
                item = _.dynamo_db.document_deserialise(raw_item)
                assert item.get('an_str'   ) == '42'
                assert item.get('user_id'  ) == user_id
                assert item.get('timestamp') > timestamp_start
                assert item.get('timestamp') < timestamp_end



