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
from osbot_aws.aws.dynamo_db.Dynamo_Table__Resource import Dynamo_Table__Resource
from osbot_aws.aws.iam.IAM_Assume_Role import IAM_Assume_Role
from osbot_utils.testing.Duration import Duration
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set
from osbot_utils.utils.Objects import type_full_name


class Dynamo_DB__with_temp_role(Dynamo_DB):

    #@print_boto3_calls()
    @cache
    def client(self):
        load_dotenv()
        service         = "dynamodb"
        action          = "*"
        resource        = "*"
        role_name       = 'osbot__temp_role_for__test_Dynamo_DB'
        policies_to_add = [dict(service=service, action=action, resource=resource)]
        iam_assume_role = IAM_Assume_Role(role_name=role_name, policies_to_add=policies_to_add)
        iam_assume_role.create_role()
        #iam_assume_role.credentials_reset()
        return iam_assume_role.boto3_client(service_name=service)


class test_Dynamo_DB(TestCase):
    dynamo_db       : Dynamo_DB
    table_name      : str
    table_key       : str
    remove_on_exit  : bool = True

    @classmethod
    def setUpClass(cls) -> None:
        cls.dynamo_db = Dynamo_DB__with_temp_role()
        cls.table_name = 'temp-table'
        cls.table_key = 'an_key'
        cls.dynamo_db.table_create(table_name=cls.table_name, key=cls.table_key)        # usually takes about 5 seconds to create


    @classmethod
    def tearDownClass(cls) -> None:
        if cls.remove_on_exit:
            cls.dynamo_db.table_delete(table_name=cls.table_name, wait_for_deletion=False)


    def test__init__(self):
        assert self.dynamo_db.client().meta.region_name == 'eu-west-1'   # make sure all temp tables are in this region

    def test_client(self):
        assert type_full_name(self.dynamo_db.client()) == 'botocore.client.DynamoDB'

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

    def test_documents_add(self):
        with self.dynamo_db as _:
            assert _.documents_all(table_name=self.table_name) == []
            document_1    = {self.table_key: 'key-1', 'answer-1': Decimal(42), 'var-1': 'goes-here'}
            document_2    = {self.table_key: 'key-2', 'answer-1': Decimal(43), 'var-2': 'and-here'}
            documents     = [document_1, document_2]
            responses_add = _.documents_add   (table_name=self.table_name, documents=documents)
            documents_all = _.documents_all   (table_name=self.table_name)
            responses_del = _.documents_delete(table_name=self.table_name, key_name=self.table_key, key_values=['key-1', 'key-2'])

            assert documents_all == [document_2, document_1]
            assert responses_add == [{'UnprocessedItems': {}}]
            assert responses_del == [{'UnprocessedItems': {}}]
            assert _.documents_all(table_name=self.table_name) == []

    def test_documents_all(self):
        assert self.dynamo_db.documents_all(table_name=self.table_name) == []


    def test_dynamo_streams(self):
        assert type_full_name(self.dynamo_db.client__dynamo_streams()) == 'botocore.client.DynamoDBStreams'

    def test_table_exists(self):
        assert self.dynamo_db.table_exists(table_name=self.table_name) is True

    def test_table_info(self):
        assert self.dynamo_db.table_info(table_name='AAAA-Not-Exists') == {}
        table_info = self.dynamo_db.table_info(table_name=self.table_name)
        assert list_set(table_info) == ['AttributeDefinitions', 'CreationDateTime', 'DeletionProtectionEnabled', 'ItemCount', 'KeySchema', 'ProvisionedThroughput', 'TableArn', 'TableId', 'TableName', 'TableSizeBytes', 'TableStatus']

    def test_table_status(self):
        assert self.dynamo_db.table_status(table_name=self.table_name) == 'ACTIVE'

    #@print_boto3_calls()
    def test_tables(self):
        tables = self.dynamo_db.tables()
        assert type(tables) == list
        assert self.table_name in tables


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
