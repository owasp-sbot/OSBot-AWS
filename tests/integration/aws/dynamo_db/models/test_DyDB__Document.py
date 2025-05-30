from decimal import Decimal

from boto3.dynamodb.types                           import Binary
from osbot_aws.aws.boto3.Capture_Boto3_Error        import capture_boto3_error
from osbot_aws.aws.dynamo_db.domains.DyDB__Table    import DyDB__Table
from osbot_aws.aws.dynamo_db.models.DyDB__Document  import DyDB__Document
from osbot_aws.testing.TestCase__Dynamo_DB__Local   import TestCase__Dynamo_DB__Local
from osbot_utils.utils.Json                         import to_json_str
from osbot_utils.utils.Misc                         import is_guid, random_text



class Temp_DyDB_Table(DyDB__Table):
    table_name = 'temp_table_for__dydb_updates'

class test_DyDB__Document(TestCase__Dynamo_DB__Local):

    temp_db_table: Temp_DyDB_Table
    document     : dict
    document_id  : str
    key_name     : str
    source_doc   : dict

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.temp_db_table = Temp_DyDB_Table(dynamo_db=cls.dynamo_db)
        cls.temp_db_table.create_table()

        #cls.temp_db_table.clear_table()         # todo: remove when finished working on DyDB__Document

        cls.key_name     = cls.temp_db_table.key_name
        cls.source_doc   = {'answer': 42, 'an_str': 'goes here', 'something_random': random_text()}
        cls.document     = cls.temp_db_table.add_document(cls.source_doc).get('document')
        cls.document_id  = cls.document.get(cls.key_name)
        cls.dydb_document = cls.temp_db_table.dydb_document(cls.document_id)



    @classmethod
    def tearDownClass(cls):
        with cls.temp_db_table as _:
            assert _.delete_document(cls.document_id) is True
            cls.temp_db_table.clear_table()                    # todo: fix test that is adding a new item
            assert _.documents_all() == []
        assert cls.temp_db_table.delete_table() is True
        super().tearDownClass()

    def test__setUpClass(self):
        with self.temp_db_table as _:
            assert _.exists() is True
            assert is_guid(self.document_id) is True
            assert _.document(self.document_id) == {**self.source_doc, 'id': self.document_id}

    def test__ctor(self):
        dydb_document = DyDB__Document(table=self.temp_db_table, document=self.document)
        assert self.document          == {**self.source_doc, 'id': self.document_id}

        with dydb_document as _:
            assert _.table         == self.temp_db_table
            assert _.document      == self.document
            assert _.key_name()    == self.key_name
            assert _.document_id() == self.document_id

        with self.temp_db_table as _:
            dydb_document = _.dydb_document(self.document_id)
            assert dydb_document.document == self.document
            assert dydb_document.document == self.dydb_document.document
            assert dydb_document.json()   == self.dydb_document.json()

    def test___repr__(self):
        assert repr(self.dydb_document) == f'[DyDB__Document]\n' + to_json_str(self.dydb_document.document)

    @capture_boto3_error
    def test_dict_set_field(self):
        with self.dydb_document as _:
            _.reset_document()

            assert _.table.document(self.document_id) == {'id': self.document_id}
            dict_field = 'an_dict'
            dict_value = {'key_1': 'value_1', 'key_2': 'value_2'}

            _.set_field(dict_field, dict_value).reload()
            assert _.document == { 'an_dict': {'key_1': 'value_1', 'key_2': 'value_2'},
                                   'id'     : self.document_id                            }

            _.dict_set_field(dict_field, 'key_1', 'changed value 1').reload()

            assert _.document == {'an_dict': {'key_1': 'changed value 1', 'key_2': 'value_2'},
                                  'id'     : self.document_id}

            _.dict_delete_field(dict_field, 'key_2').reload()

            assert _.document == {'an_dict': {'key_1': 'changed value 1'},
                                 'id'     : self.document_id}

            _.set_document(self.source_doc)

    @capture_boto3_error
    def test_dict_increase_field(self):
        with self.dydb_document as _:
            _.reset_document()

            assert _.table.document(self.document_id) == {'id': self.document_id}
            dict_field = 'user_traffic'
            dict_value = { 'web_calls': 10, 'api_calls': 10 }
            _.add_field(dict_field, dict_value)
            _.dict_set_field('user_traffic', 'web_calls', -30)
            _.dict_set_field('user_traffic', 'another'  ,   7)
            _.dict_update_counter('user_traffic', 'api_calls', 36)
            _.dict_update_counter('user_traffic', 'api_calls', -4)
            assert _.reload() == { 'id'          : _.document_id()          ,
                                   'user_traffic': { 'another': Decimal('7'),
                                   'api_calls'   : Decimal('42')            ,
                                   'web_calls'   : Decimal('-30')}          }


    def test_deserialize_value(self):
        value     = {"an_str": 'here', 'an_int': 42, "some_bytes": b"are there", "an_dict": {"is": "here"}}
        value_raw = {'M': {'an_dict'   : {'M': {'is': {'S': 'here' }}},
                           'an_int'    : {'N': '42'                  },
                           'an_str'    : {'S': 'here'                },
                           'some_bytes': {'B': b'are there'          }}}
        with self.dydb_document as _:
            assert _.serialize_value  (value                         ) == value_raw
            assert _.deserialize_value(value_raw                     ) == value
            assert _.serialize_value  (_.deserialize_value(value_raw)) == value_raw
            assert _.deserialize_value(_.serialize_value  (value    )) == value


    def test_add_to_list(self):
        with self.dydb_document as _:
            assert _.fields_names() == ['an_str', 'answer', 'id', 'something_random']
            new_list    = 'a_list'
            new_value_1 = 'the answer'
            new_value_2 = 'is 42'
            _.add_to_list(new_list, new_value_1)
            assert _.fields_names() == ['an_str', 'answer', 'id', 'something_random']
            assert _.reload()                    == {**self.document, new_list: [new_value_1]}
            _.add_to_list(new_list, new_value_2)
            assert _.reload()                    == {**self.document, new_list: [new_value_1, new_value_2]}
            _.delete_field(new_list)
            _.reload()
            assert _.fields_names() == ['an_str', 'answer', 'id', 'something_random']

            new_value_3 = {'action': 'connect'   }
            new_value_4 = {'action': 'disconnect'}

            _.add_to_list(new_list, new_value_3)
            _.add_to_list(new_list, new_value_4)
            assert _.reload() == {**self.document, new_list: [new_value_3, new_value_4]}

            _.add_to_list(new_list, new_value_1)
            _.add_to_list(new_list, new_value_2)

            _.delete_item_from_list(new_list,1)
            assert _.reload() == {**self.document, new_list: [new_value_3, new_value_1, new_value_2]}
            _.delete_item_from_list(new_list, 1)
            assert _.reload() == {**self.document, new_list: [new_value_3, new_value_2             ]}
            _.delete_field(new_list)

    def test_add_to_set(self):
        with self.dydb_document as _:
            _.add_field('an_set', {'an', 'set'})

            _.add_to_set('an_set', 'new item')
            assert _.field('an_set') == {'set', 'an', 'new item'}
            _.delete_from_set('an_set', 'an')
            assert _.field('an_set') == {'set', 'new item'}

            _.set_document(self.source_doc)

    def test_reset_document(self):
        with self.dydb_document as _:
            assert _.reset_document()               .document == {self.key_name: self.document_id}
            assert _.set_document  (self.source_doc).document == self.document

    def test_set_field(self):
        with self.dydb_document as _:
            assert _.fields_names() == ['an_str', 'answer', 'id', 'something_random']
            new_field  = 'something_new'
            new_value  = 'with a new value'
            add_result = _.set_field(new_field, new_value)
            assert add_result == _
            assert _.fields_names() == ['an_str', 'answer', 'id', 'something_random']

            assert _.reload() == {**self.document, new_field:new_value}
            assert _.fields_names() == ['an_str', 'answer', 'id', new_field, 'something_random']

            assert _.document != self.document
            assert _.document == {**self.document, new_field:new_value}

            assert _.delete_field(new_field) is True
            _.reload()
            assert _.fields_names() == ['an_str', 'answer', 'id', 'something_random']
            assert _.document                == self.document
            assert _.delete_field(new_field) is False


    def test_increment_field(self):
        with self.dydb_document as _:
            assert _.fields_names() == ['an_str', 'answer', 'id', 'something_random']

            _.increment_field('answer', 1).reload()
            _.increment_field('answer', Decimal(9)).reload()
            assert _.document.get('answer'       ) == 52
            _.increment_field('answer', -42).reload()
            assert _.document.get('answer'       ) == 10

            _.increment_field('new_field', Decimal(7)).reload()
            assert _.fields_names() == ['an_str', 'answer', 'id', 'new_field', 'something_random']
            assert _.document.get('new_field') == Decimal(7)

    def test_increment_field__with_condition(self):
        with self.dydb_document as _:
            field_name = 'an_counter'
            _.set_field(field_name, 2)
            assert _.increment_field__if_existing_value_bigger_than(field_name, -1, 0) is True
            assert _.field(field_name) == 1
            assert _.increment_field__if_existing_value_bigger_than(field_name, -1, 0) is True
            assert _.field(field_name) == 0
            assert _.increment_field__if_existing_value_bigger_than(field_name, -1, 0) is False

    def test_delete_elements_from_set(self):
        with self.dydb_document as _:
            _.add_field('an_string_set' , {'set_1' , 'set_2', 'set_3', 'set_4'}                         )
            _.add_field('an_int_set'    , {1, 2,3,4,5})
            _.add_field('an_bytes_set'  , {b'bytes_1' , b'bytes_2', b'bytes_3', b'bytes_4'} )
            _.delete_from_set('an_string_set', 'set_2')
            _.delete_from_set('an_bytes_set', b'bytes_2')
            _.delete_elements_from_set('an_int_set'   , {3, 4}    ).reload()
            #pprint(_.reload())
            document = _.reload()
            document['an_string_set'] = sorted(document['an_string_set'])
            document['an_int_set'   ] = sorted(document['an_int_set'   ])
            document['an_bytes_set' ] = sorted(document['an_bytes_set'], key=lambda x: bytes(x))        # need to covert to bytes since Binary doesn't support <

            assert document == { 'an_bytes_set'    : [ Binary(b'bytes_1')   ,
                                                       #Binary(b'bytes_2')  ,           # removed by _.delete_element_from_set('an_bytes_set'  , b'bytes_2')
                                                       Binary(b'bytes_3')   ,
                                                       Binary(b'bytes_4')   ],
                                 'an_int_set'      : [ Decimal('1') ,
                                                       Decimal('2') ,
                                                       #Decimal('3'),                   # removed by _.delete_elements_from_set('an_int_set'   , {3, 4}    )
                                                       #Decimal('4'),
                                                       Decimal('5')],
                                 'an_str'          : 'goes here'    ,
                                 'an_string_set'   : [ 'set_1'      ,
                                                       #'set_2'     ,                   # removed by _.delete_element_from_set('an_string_set' , 'set_2'   )
                                                       'set_3'      ,
                                                       'set_4'      ],
                                 'answer'          : Decimal('42')  ,
                                 'id'              : self.document_id,
                                 'something_random': self.document.get('something_random')}
            with self.assertRaises(TypeError) as context:
                _.delete_elements_from_set('aaa', 'aaaa')
            assert context.exception.args[0] == ("in 'build__delete_elements_from_set' the 'elements' parameter must be an "
                                                 "'set', but it was an 'str'")

    def test__multiple_updates_in_one_call(self):
        with self.dydb_document as _:
            value_1 = random_text('value_1')
            value_2 = random_text('value_2')
            value_3 = random_text('value_3')
            update_expression           = "SET #attribute1 = :val0, #attribute2 = :val1, #attribute3 = :val2"
            expression_attribute_names  = { "#attribute1": "attribute1",
                                            "#attribute2": "attribute2",
                                            "#attribute3": "attribute3"}

            expression_attribute_values = { ":val0": _.serialize_value(value_1),
                                            ":val1": _.serialize_value(value_2),
                                            ":val2": _.serialize_value(value_3)}
            query_builder = _.db_query_builder()
            query_builder.update_expression             = update_expression
            query_builder.expression_attribute_names    = expression_attribute_names
            query_builder.expression_attribute_values   = expression_attribute_values
            query_kwargs = query_builder.build()
            _.update_item(**query_kwargs)
            assert _.fields('attribute1', 'attribute2', 'attribute3') == {'attribute1': value_1,
                                                                          'attribute2': value_2,
                                                                          'attribute3': value_3}
            _.set_document(self.source_doc)

    # use this to intercept the DyDB__Query__Builder.build call
    # def after_call(return_value, *args, **kwargs):
    #     # return_value['ExpressionAttributeValues'][':zero'] =  {'N': '0'}
    #     # return_value['ConditionExpression'] = '#field_name > :zero'
    #     return return_value
    #
    # hook_method = (Hook_Method(target_module=DyDB__Query__Builder, target_method='build')
    #                 .add_on_after_call(after_call))
    # with hook_method:
