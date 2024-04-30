
from osbot_aws.aws.dynamo_db.domains.DyDB__Table import DyDB__Table
from osbot_aws.aws.dynamo_db.models.DyDB__Document import DyDB__Document
from osbot_aws.testing.TestCase__Dynamo_DB import TestCase__Dynamo_DB
from osbot_utils.utils.Dev import pprint
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

        # cls.temp_db_table.clear_table()         # todo: remove when finished working on DyDB__Document

        cls.key_name     = cls.temp_db_table.key_name
        cls.source_doc   = {'answer': 45, 'an_str': 'goes here', 'something_random': random_text()}
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

    def test_add_field(self):
        with self.dydb_document as _:
            assert _.fields() == ['an_str', 'answer', 'id', 'something_random']
            new_field  = 'something_new'
            new_value  = 'with a new value'
            add_result = _.add_field(new_field, new_value)
            assert add_result == {'Attributes': {new_field: {'S': new_value}}}
            assert _.fields() == ['an_str', 'answer', 'id', 'something_random']

            assert _.reload() == {**self.document, new_field:new_value}
            assert _.fields() == ['an_str', 'answer', 'id', new_field, 'something_random']








