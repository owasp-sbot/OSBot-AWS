from unittest import TestCase

from osbot_aws.aws.dynamo_db.models.DyDB__Query__Builder import DyDB__Query__Builder
from osbot_utils.utils.Misc import random_guid, random_text


class test_DyDB__Query__Builder(TestCase):
    db_query_builder : DyDB__Query__Builder
    key_name         : str      = random_text('id')
    key_value        : str      = random_guid()
    table_name       : str      = random_text('an_table')
    @classmethod
    def setUpClass(cls):
        cls.db_query_builder = DyDB__Query__Builder(table_name=cls.table_name, key_name=cls.key_name, key_value=cls.key_value)

    def test__setUpClass(self):
        assert self.db_query_builder.__locals__() == {'key_name'  : self.key_name   ,
                                                      'key_value' : self.key_value  ,
                                                      'table_name': self.table_name }


    def test_build__add_to_list(self):
        list_field_name = random_text('list_field_name')
        new_list_element = random_text('new_list_element')
        expected_query   = {'ExpressionAttributeValues': {':empty_list': {'L': []},
                                                           ':new_element': {'L': [{'S': new_list_element}]}},
                             'Key': {self.key_name: {'S': self.key_value}},
                             'ReturnValues': 'UPDATED_NEW',
                             'TableName': self.table_name,
                             'UpdateExpression': f'SET {list_field_name} = '
                                                 f'list_append(if_not_exists({list_field_name}, '
                                                 ':empty_list), :new_element)'}
        assert self.db_query_builder.build__add_to_list(list_field_name,new_list_element) == expected_query