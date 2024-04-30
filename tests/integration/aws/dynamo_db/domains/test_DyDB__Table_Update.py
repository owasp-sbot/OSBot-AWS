from osbot_aws.aws.boto3.Capture_Boto3_Error import capture_boto3_error
from osbot_aws.aws.dynamo_db.domains.DyDB__Table        import DyDB__Table
from osbot_aws.aws.dynamo_db.domains.DyDB__Table_Update import DyDB__Table_Update
from osbot_aws.testing.TestCase__Dynamo_DB              import TestCase__Dynamo_DB
from osbot_utils.utils.Dev                              import pprint
from osbot_utils.utils.Misc                             import is_guid


class Temp_DyDB_Table(DyDB__Table_Update):
    table_name = 'temp_table_for__dydb_updates'

class test_Dynamo_DB__Update(TestCase__Dynamo_DB):
    temp_db_table   : Temp_DyDB_Table
    document_id       : str

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.temp_db_table = Temp_DyDB_Table(dynamo_db=cls.dynamo_db)
        cls.temp_db_table.create_table()
        cls.document_id     = cls.temp_db_table.add_document({}).get('document').get('id')

    @classmethod
    def tearDownClass(cls):
        with cls.temp_db_table as _:
            assert _.delete_document(cls.document_id) is True
            assert _.documents_all() == []

    def test__setUp(self):
        with self.temp_db_table as _:
            assert _.exists()                    is True
            assert is_guid(self.document_id)     is True
            assert _.document(self.document_id)  == {'id': self.document_id}

    @capture_boto3_error
    def test_update_add_field(self):

        with (self.temp_db_table as _):
            field_name  = 'an_field'
            field_value = 'with this value'
            result      = _.update_add_field(self.document_id,field_name, field_value)
            assert result                        == {'Attributes': { field_name: {'S':  field_value }}}
            assert  _.document(self.document_id) == {field_name: field_value, 'id': self.document_id}
