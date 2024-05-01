from decimal import Decimal
from unittest import TestCase

from osbot_aws.aws.dynamo_db.models.DyDB__Query__Builder import DyDB__Query__Builder
from osbot_utils.utils.Misc                              import random_guid, random_text

class test_DyDB__Query__Builder(TestCase):
    db_query_builder : DyDB__Query__Builder
    key_name         : str      = random_text('id')
    key_value        : str      = random_guid()
    table_name       : str      = random_text('an_table')


    def setUp(self):
        self.db_query_builder = DyDB__Query__Builder(table_name=self.table_name, key_name=self.key_name, key_value=self.key_value)

    def test__setUpClass(self):
        assert self.db_query_builder.__locals__() == {'key_name'                    : self.key_name   ,
                                                      'key_value'                   : self.key_value  ,
                                                      'kwargs'                      : {}              ,
                                                      'expression_attribute_values' : {}              ,
                                                      'expression_attribute_names'  : {}              ,
                                                      'return_values'               : 'NONE'          ,
                                                      'table_name'                  : self.table_name ,
                                                      'update_expression'           : ''              }



    def test_build__add_to_list(self):
        list_field_name = random_text('list_field_name')
        new_list_element = random_text('new_list_element')
        expected_query   = {'ExpressionAttributeValues' : {':empty_list': {'L': []},
                                                          ':new_element': {'L': [{'S': new_list_element}]}},
                            'Key'                       : {self.key_name: {'S': self.key_value}},
                            'ReturnValues'              : 'NONE',
                            'TableName'                 : self.table_name,
                            'UpdateExpression'          : f'SET {list_field_name} = '
                                                          f'list_append(if_not_exists({list_field_name}, '
                                                           ':empty_list), :new_element)'}
        assert self.db_query_builder.build__add_to_list(list_field_name, new_list_element) == expected_query

    def test_build__dict_delete_field(self):
        dict_field = random_text('dict_field')
        field_key  = random_text('field_key')
        expected_query = {'TableName'               : self.table_name,
                          'Key'                     : {self.key_name: {'S': self.key_value}},
                          'UpdateExpression'        : f'REMOVE #dict_field.#key',
                          'ExpressionAttributeNames': {'#dict_field': dict_field, '#key': field_key},
                          'ReturnValues'            : 'NONE'}

        assert self.db_query_builder.build__dict_delete_field(dict_field, field_key) == expected_query

    def test_build__dict_set_field(self):
        dict_field = random_text('dict_field')
        field_key = random_text('field_key')
        field_value = random_text('field_value')
        expected_query = {'TableName'                : self.table_name,
                          'Key'                      : {self.key_name: {'S': self.key_value}},
                          'UpdateExpression'         : f'SET #dict_field.#key = :val',
                          'ExpressionAttributeNames' : {'#dict_field': dict_field, '#key': field_key},
                          'ExpressionAttributeValues': {':val': {'S': field_value}},
                          'ReturnValues'             : 'NONE'}
        assert self.db_query_builder.build__dict_set_field(dict_field, field_key, field_value) == expected_query

    def test_build__delete_field(self):
        field_name = random_text('field_name')

        expected_query = {'TableName'               : self.table_name,
                          'Key'                     : {self.key_name: {'S': self.key_value}},
                          'UpdateExpression'        : f'REMOVE #field_name',
                          'ExpressionAttributeNames': {'#field_name': field_name},
                          'ReturnValues'            : 'NONE'}
        assert self.db_query_builder.build__delete_field(field_name) == expected_query

    def test_build__delete_item_from_list(self):
        list_field_name = random_text('list_field_name')
        item_index = 10  # example index
        expected_query = {'TableName'               : self.table_name,
                          'Key'                     : {self.key_name: {'S': self.key_value}},
                          'UpdateExpression'        : f'REMOVE #list_field_name[{item_index}]',
                          'ExpressionAttributeNames': {'#list_field_name': list_field_name},
                          'ReturnValues'            : 'NONE'}
        assert self.db_query_builder.build__delete_item_from_list(list_field_name, item_index) == expected_query
        item_index = Decimal(10)
        assert self.db_query_builder.build__delete_item_from_list(list_field_name, item_index) == expected_query

        with self.assertRaises(TypeError) as context:
            assert self.db_query_builder.build__delete_item_from_list(list_field_name, 'aaa') #check for query injection
        assert context.exception.args == ("in 'build__delete_item_from_list' the 'item_index' parameter must be an "
                                          "'int, Decimal', but it was an 'str'",)


    def test_build__delete_elements_from_set(self):
        set_field_name = random_text('set_field_name')
        elements = {'element1', 'element2'}
        expected_query = {'TableName'                : self.table_name,
                          'Key'                      : {self.key_name: {'S': self.key_value}},
                          'UpdateExpression'         : f'DELETE #set_field_name :elementsToRemove',
                          'ExpressionAttributeNames' : {'#set_field_name': set_field_name},
                          'ExpressionAttributeValues': {':elementsToRemove': {'SS': list(elements)}},
                          'ReturnValues'             : 'NONE'}
        assert self.db_query_builder.build__delete_elements_from_set(set_field_name, elements) == expected_query

        with self.assertRaises(TypeError) as context:
            assert self.db_query_builder.build__delete_elements_from_set(set_field_name, 'aaa') #check for query injection
        assert context.exception.args == ("in 'build__delete_elements_from_set' the 'elements' parameter must be an "
                                          "'set', but it was an 'str'",)


    def test_build__set_field(self):
        field_name = random_text('field_name')
        field_value = random_text('field_value')
        expected_query = {'TableName'                : self.table_name,
                          'Key'                      : {self.key_name: {'S': self.key_value}},
                          'UpdateExpression'         : f'SET #field_name = :field_value',
                          'ExpressionAttributeNames' : {'#field_name': field_name},
                          'ExpressionAttributeValues': {':field_value': {'S': field_value}},
                          'ReturnValues'             : 'NONE'}
        assert self.db_query_builder.build__set_field(field_name, field_value) == expected_query

    def test_build__update_counter(self):
        field_name = random_text('field_name')
        increment_by = 1
        expected_query = {'TableName'                : self.table_name,
                          'Key'                      : {self.key_name: {'S': self.key_value}},
                          'UpdateExpression'         : f'ADD #field_name :inc',
                          'ExpressionAttributeNames' : {'#field_name': field_name},
                          'ExpressionAttributeValues': {':inc': {'N': str(increment_by)}},
                          'ReturnValues'             : 'NONE'  }
        assert self.db_query_builder.build__update_counter(field_name, increment_by) == expected_query

        with self.assertRaises(ValueError) as context:
            assert self.db_query_builder.build__update_counter(field_name, 'aaa') #check for query injection
        assert context.exception.args == ('in build__update_counter increment value must be an integer and it was an '
                                          "<class 'str'>",)