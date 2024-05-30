import base64
import json
import os
import unittest
from contextlib import contextmanager
from decimal import Decimal
from functools import cache
from unittest import TestCase

from dotenv import load_dotenv

from osbot_aws.aws.boto3.View_Boto3_Rest_Calls import print_boto3_calls
from osbot_aws.aws.dynamo_db.Dynamo_DB import Dynamo_DB
from osbot_aws.aws.dynamo_db.Dynamo_DB__with_temp_role import Dynamo_DB__with_temp_role
from osbot_aws.aws.dynamo_db.Dynamo_Table__Resource import Dynamo_Table__Resource
from osbot_aws.aws.iam.IAM_Assume_Role import IAM_Assume_Role
from osbot_aws.testing.Pytest import skip_pytest___aws_pytest_user_name__is_not_set
from osbot_aws.testing.TestCase__Boto3_Cache import TestCase__Boto3_Cache
from osbot_utils.testing.Duration import Duration
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set, random_string
from osbot_utils.utils.Objects import type_full_name

class test_Dynamo_DB(TestCase):
    dynamo_db       : Dynamo_DB
    table_name      : str
    table_key       : str
    remove_on_exit  : bool = False

    @classmethod
    def setUpClass(cls) -> None:
        skip_pytest___aws_pytest_user_name__is_not_set()
        cls.dynamo_db = Dynamo_DB__with_temp_role()
        cls.table_name = 'temp-table'
        cls.table_key = 'an_key'
        cls.dynamo_db.table_create(table_name=cls.table_name, key_name=cls.table_key)        # usually takes about 5 seconds to create


    @classmethod
    def tearDownClass(cls) -> None:
        if cls.remove_on_exit:
            cls.dynamo_db.table_delete(table_name=cls.table_name, wait_for_deletion=False)


    def test__init__(self):
        assert self.dynamo_db.client().meta.region_name == 'eu-west-1'   # make sure all temp tables are in this region

    # main methods

    #@print_boto3_calls()
    def test_document_add(self):
        with self.dynamo_db as _:
            assert _.documents_all(table_name=self.table_name) == []
            document_1 = { self.table_key: 'key-1', 'answer-1': Decimal(42) ,'var-1': 'goes-here'}
            document_2 = { self.table_key: 'key-2', 'answer-1': Decimal(43), 'var-2': 'and-here'}
            _.document_add(table_name=self.table_name, document=document_1)
            _.document_add(table_name=self.table_name, document=document_2)
            all_items = _.documents_all(table_name=self.table_name)
            assert all_items == [document_2, document_1]

            assert _.document(table_name=self.table_name, key_name=self.table_key, key_value='key-1') == document_1
            assert _.document(table_name=self.table_name, key_name=self.table_key, key_value='key-2') == document_2

            assert _.documents_keys(table_name=self.table_name, key_name=self.table_key) == ['key-2', 'key-1']

            _.document_delete(table_name=self.table_name, key_name=self.table_key, key_value='key-1')
            _.document_delete(table_name=self.table_name, key_name=self.table_key, key_value='key-2')
            assert _.documents_all(table_name=self.table_name) == []

    def test_document_update(self):
        with self.dynamo_db as _:
            key_value = random_string(prefix='an_key')
            document = {self.table_key: key_value, 'answer-1': Decimal(42), 'var-1': 'goes-here'}
            _.document_add(table_name=self.table_name, document=document)
            assert _.document(table_name=self.table_name, key_name=self.table_key, key_value=key_value) == document
            update_result = _.document_update(table_name=self.table_name, key_name=self.table_key, key_value=key_value, update_data={'answer-1': Decimal(43)})
            assert update_result == {'Attributes': {'answer-1': {'N': '43'}}}
            updated_items = update_result.get('Attributes')
            document.update(updated_items)
            assert document == {self.table_key: key_value, 'answer-1': {'N': '43'}, 'var-1': 'goes-here'}
            updated_items_deserialised = _.document_deserialize(updated_items)
            assert updated_items_deserialised == {'answer-1': Decimal('43')}
            document.update(updated_items_deserialised)
            assert document == {self.table_key: key_value, 'answer-1': Decimal(43), 'var-1': 'goes-here'}
            assert _.document(table_name=self.table_name, key_name=self.table_key, key_value=key_value) == document
            assert _.document_delete(table_name=self.table_name, key_name=self.table_key, key_value=key_value) is True

    def test_document_update__all__possible_data_types(self):
        with self.dynamo_db as _:
            key_value = 'data_types_key'
            # Initial document with various data types
            document = { self.table_key: key_value,
                        'string_attr': 'hello',
                        'number_attr': Decimal(123),
                        'binary_attr': base64.b64encode(b'binary data'),
                        'boolean_attr': True,
                        'null_attr': None,
                        'list_attr': ['a', Decimal(1), False],
                        'map_attr': {'nested_string': 'world', 'nested_number': Decimal(456)},
                        'string_set_attr': set(['a', 'b', 'c']),
                        'number_set_attr': set([Decimal(1), Decimal(2), Decimal(3)]), }

            # Add the document
            _.document_add(table_name=self.table_name,  document=document)
            assert _.document(table_name=self.table_name, key_name=self.table_key, key_value='data_types_key') == document

            # Update some of the data types
            update_data = {
                'string_attr': 'hello world',
                'number_attr': Decimal(321),
                'binary_attr': base64.b64encode(b'updated binary data'),
                'boolean_attr': False,
                'null_attr': None,  # DynamoDB doesn't store nulls; used here for completeness
                'list_attr': ['x', Decimal(9), True],
                'map_attr': {'nested_string': 'universe', 'nested_number': Decimal(654)},
                'string_set_attr': set(['d', 'e', 'f']),
                'number_set_attr': set([Decimal(4), Decimal(5), Decimal(6)]),
            }

            # Update the document
            update_result = _.document_update(table_name=self.table_name, key_name=self.table_key, key_value='data_types_key', update_data=update_data)

            # Fetch and assert updated document
            updated_document = _.document(table_name=self.table_name, key_name=self.table_key, key_value='data_types_key')

            # Prepare expected updated document (excluding null_attr as DynamoDB does not store nulls)
            expected_updated_document = document.copy()
            expected_updated_document.update(update_data)

            # Deserialize binary data for comparison
            expected_updated_document['binary_attr'] = base64.b64decode(expected_updated_document['binary_attr'])
            updated_document['binary_attr'] = base64.b64decode(updated_document['binary_attr'].value)

            assert updated_document == expected_updated_document
            assert _.document_delete(table_name=self.table_name, key_name=self.table_key, key_value=key_value) is True


    def test_documents_add(self):
        with self.dynamo_db as _:
            assert _.documents_all(table_name=self.table_name) == []
            document_1    = {self.table_key: 'key-1', 'answer-1': Decimal(42), 'var-1': 'goes-here'}
            document_2    = {self.table_key: 'key-2', 'answer-1': Decimal(43), 'var-2': 'and-here'}
            documents     = [document_1, document_2]
            responses_add = _.documents_add   (table_name=self.table_name, documents=documents)
            documents_all = _.documents_all   (table_name=self.table_name)
            responses_del = _.documents_delete(table_name=self.table_name, key_name=self.table_key, keys_values=['key-1', 'key-2'])

            assert documents_all == [document_2, document_1]
            assert responses_add == dict(documents=documents,responses=[{'UnprocessedItems': {}}])
            assert responses_del == [{'UnprocessedItems': {}}]
            assert _.documents_all(table_name=self.table_name) == []



    def test_documents_delete_all(self):
        assert self.dynamo_db.documents_delete_all(table_name=self.table_name, key_name=self.table_key) == {'delete_result': [], 'delete_status': True, 'deleted_keys': []}


    #@print_boto3_calls()


# @unittest.skip('this is not working as expected (namely the `test_streams` part)')
# class test_Dynamo_Streams(unittest.TestCase):
#
#     def setUp(self):
#         self.table_name        = 'temp-table-with-streams'  #Misc.random_string_and_numbers(prefix='temp-table-with-streams_')
#         self.table_key         = 'an_field'
#         with_streams      = True
#         self.dynamo_table = Dynamo_Table(self.table_name, self.table_key)
#         self.dynamo       = Dynamo()
#         if self.dynamo_table.exists() is False:
#             self.dynamo.create(self.table_name, self.table_key, with_streams)
#
#     def test_stream_arn(self):
#         assert self.dynamo_table.stream_arn().startswith('arn:aws:dynamodb:') is True
#
#     def test_stream_info(self):
#         Dev.pprint(self.dynamo_table.stream_info())
#
#     def test_stream_get_data_latest(self):
#         self.dynamo_table.add({ self.table_key : 'key-1', 'answer-1': 42 })
#         Dev.pprint(self.dynamo_table.stream_get_data_latest())
#
#     def test_streams(self):
#         assert len(self.dynamo.streams()) > 1
