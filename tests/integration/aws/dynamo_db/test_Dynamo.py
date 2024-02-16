import json
import os
import unittest
from contextlib import contextmanager
from functools import cache
from unittest import TestCase

import boto3
import botocore
import pytest
from dotenv import load_dotenv

from osbot_aws.aws.boto3.View_Boto3_Rest_Calls import print_boto3_calls
from osbot_aws.aws.dynamo_db.Dynamo_DB import Dynamo_DB
from osbot_aws.aws.dynamo_db.Dynamo_Table__Resource import Dynamo_Table__Resource
from osbot_aws.aws.iam.IAM import IAM
from osbot_aws.aws.iam.IAM_Assume_Role import IAM_Assume_Role
from osbot_aws.aws.iam.STS import STS
from osbot_utils.testing.Duration import Duration
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Objects import type_full_name


class Dynamo_DB__with_temp_role(Dynamo_DB):

    #@print_boto3_calls()
    @cache
    def client(self):
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

    def setUp(self):
        load_dotenv()
        #os.environ['AWS_DEFAULT_REGION'] = 'eu-west-2'
        self.dynamo_db = Dynamo_DB__with_temp_role()

    def test_dynamo(self):
        assert type_full_name(self.dynamo_db.client()) == 'botocore.client.DynamoDB'

    def test_dynamo_streams(self):
        assert type_full_name(self.dynamo_db.dynamo_streams()) == 'botocore.client.DynamoDBStreams'

    #@print_boto3_calls()
    def test_list(self):
        pprint(self.dynamo_db.client().meta.region_name)
        tables = self.dynamo_db.list()
        assert type(tables) == list


#todo: wire up back the tests below


# class Test_Dynamo(unittest.TestCase):
#     def setUp(self):
#         self.dynamo     = Dynamo()
#         self.table_name = 'temp-table'
#         self.table_key  = 'an_field'
#         self.table      = Dynamo_Table(self.table_name,self.table_key)
#
#     def test_create(self):
#         if self.table.exists() is False:
#             self.dynamo.create(self.table_name, 'an_field')
#             assert self.table.exists()                       is True
#             assert self.table.info()['Table']['TableName']   == self.table_name
#
#     def test_list(self):
#         result = self.dynamo.list()
#         assert 'temp-table' in result


@unittest.skip('to wire up once the IAM privages are in place')
class test_Dynamo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dynamo = Dynamo_DB()
        table_name = 'temp-table'
        table_key = 'an_field'
        table = Dynamo_Table__Resource(table_name, table_key)

        if table.exists() is False:
            dynamo.create(table_name, 'an_field')
            assert table.exists() is True
            assert table.info()['Table']['TableName'] == table_name

        assert 'temp-table' in dynamo.list()

    @classmethod
    def tearDownClass(cls):
        dynamo = Dynamo_DB()
        table_name = 'temp-table'
        table_key = 'an_field'
        table = Dynamo_Table__Resource(table_name, table_key)

        if table.exists():
            dynamo.delete(table_name)
            assert table.exists() is False
            assert table.info()   is None

    def setUp(self):
        self.table_name =  'temp-table'
        self.table_key  = 'an_field'
        self.table = Dynamo_Table__Resource(self.table_name, self.table_key)

    def test_add(self):
        self.table.add({ self.table_key : 'key-1', 'answer-1': 42 })
        self.table.add({ self.table_key : 'key-2', 'answer-2': -1  })

    def test_add_delete_batch(self):
        assert self.table.keys() == ['key-2', 'key-1']
        items = [{ self.table_key: 'key-3', 'answer-1': 42 },
                 { self.table_key: 'key-4', 'answer-1': 42 }]
        self.table.add_batch(items)
        keys = self.table.keys(use_cache=False)
        assert len(keys) == 4
        assert 'key-3'   in  keys

        items = [ { self.table_key: 'key-3'},
                  { self.table_key: 'key-4' }]
        self.table.delete_batch(items)

        keys = self.table.keys()
        assert len(keys) == 4

    def test_delete(self):
        self.table.add({self.table_key: 'key-5', 'answer-1': 42})
        assert self.table.get('key-5') == {self.table_key: 'key-5', 'answer-1': 42}

        self.table.delete('key-5')
        assert self.table.get('key-5') == None

    def test_keys(self):
        result = self.table.keys()
        assert result == ['key-2', 'key-1']

    def test_info(self):
        result = self.table.info()
        assert result['Table']['AttributeDefinitions'] == [{'AttributeName': 'an_field', 'AttributeType': 'S'}]
        assert result['Table']['TableName'           ] == self.table_name

    def test_get(self):
        result = self.table.get('key-1')
        assert result == {'answer-1': 42, 'an_field': 'key-1'}

    def test_get_batch(self):
        self.table.chuck_size = 1
        keys = self.table.keys()
        results = self.table.get_batch(keys)

        assert next(results) == [{'answer-2': -1, 'an_field': 'key-2'}]
        assert next(results) == [{'answer-1': 42, 'an_field': 'key-1'}]

    def test_status(self):
        assert self.table.status() == 'ACTIVE'


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
