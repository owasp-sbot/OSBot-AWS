from decimal import Decimal

from boto3.dynamodb.types import Binary

from osbot_aws.aws.boto3.Capture_Boto3_Error import capture_boto3_error
from osbot_aws.aws.boto3.View_Boto3_Rest_Calls import print_boto3_calls
from osbot_aws.aws.dynamo_db.domains.DyDB__Table import DyDB__Table
from osbot_aws.aws.dynamo_db.models.DyDB__Document import DyDB__Document
from osbot_aws.testing.TestCase__Dynamo_DB import TestCase__Dynamo_DB
from osbot_utils.utils.Dev import pprint, jprint
from osbot_utils.utils.Json import to_json_str
from osbot_utils.utils.Misc import is_guid, random_text


class Temp_DyDB_Table(DyDB__Table):
    table_name = 'temp_table_for__dydb_updates'

class test_DyDB__Document(TestCase__Dynamo_DB):

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
            assert _.documents_all() == []

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
            assert _.fields() == ['an_str', 'answer', 'id', 'something_random']
            new_list    = 'a_list'
            new_value_1 = 'the answer'
            new_value_2 = 'is 42'
            assert _.add_to_list(new_list, new_value_1) == {new_list: {'L': [{'S': new_value_1}]}}
            assert _.fields()                           == ['an_str', 'answer', 'id', 'something_random']
            assert _.reload()                           == {**self.document, new_list: [new_value_1]}
            assert _.add_to_list(new_list, new_value_2) == {new_list: {'L': [{'S': new_value_1},{'S': new_value_2}]}}
            assert _.reload()                           == {**self.document, new_list: [new_value_1, new_value_2]}

            _.delete_field(new_list)
            assert _.fields() == ['an_str', 'answer', 'id', 'something_random']
            new_value_3 = {'action': 'connect'   }
            new_value_4 = {'action': 'disconnect'}

            assert _.add_to_list(new_list, new_value_3) == {new_list: {'L': [{'M': {'action': {'S': 'connect'}}}]}}
            _.add_to_list(new_list, new_value_4)
            assert _.reload() == {**self.document, new_list: [new_value_3, new_value_4]}

            _.add_to_list(new_list, new_value_1)
            _.add_to_list(new_list, new_value_2)

            _.delete_item_from_list(new_list,1)
            assert _.reload() == {**self.document, new_list: [new_value_3, new_value_1, new_value_2]}
            _.delete_item_from_list(new_list, 1)
            assert _.reload() == {**self.document, new_list: [new_value_3, new_value_2             ]}

            _.delete_field(new_list)

    def test_reset_document(self):
        with self.dydb_document as _:
            assert _.reset_document()               .document == {self.key_name: self.document_id}
            assert _.set_document  (self.source_doc).document == self.document





    def test_set_field(self):
        with self.dydb_document as _:
            assert _.fields() == ['an_str', 'answer', 'id', 'something_random']
            new_field  = 'something_new'
            new_value  = 'with a new value'
            add_result = _.set_field(new_field, new_value)
            assert add_result == _
            assert _.fields() == ['an_str', 'answer', 'id', 'something_random']

            assert _.reload() == {**self.document, new_field:new_value}
            assert _.fields() == ['an_str', 'answer', 'id', new_field, 'something_random']

            assert _.document != self.document
            assert _.document == {**self.document, new_field:new_value}

            assert _.delete_field(new_field) is True
            assert _.fields()                == ['an_str', 'answer', 'id', 'something_random']
            assert _.document                == self.document
            assert _.delete_field(new_field) is False


    def test_update_counter(self):
        with self.dydb_document as _:
            assert _.fields() == ['an_str', 'answer', 'id', 'something_random']

            _.update_counter('answer', 1).reload()
            assert _.document.get('answer') == 43
            _.update_counter('answer', -42).reload()
            assert _.document.get('answer') == 1

            _.update_counter('new_field', Decimal(7)).reload()
            assert _.fields() == ['an_str', 'answer', 'id', 'new_field', 'something_random']
            assert _.document.get('new_field') == Decimal(7)

    @capture_boto3_error
    def test_delete_elements_from_set(self):
        with self.dydb_document as _:
            _.add_field('an_string_set' , {'set_1' , 'set_2', 'set_3', 'set_4'}                         )
            _.add_field('an_int_set'    , {1, 2,3,4,5})
            _.add_field('an_bytes_set'  , {b'bytes_1' , b'bytes_2', b'bytes_3', b'bytes_4'} )
            _.delete_element_from_set('an_string_set' , 'set_2'   )
            _.delete_element_from_set('an_bytes_set'  , b'bytes_2')
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



