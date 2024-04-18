import uuid

from osbot_aws.aws.dynamo_db.Dynamo_DB import Dynamo_DB
from osbot_aws.aws.dynamo_db.Dynamo_DB__Record import Dynamo_DB__Record
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.decorators.methods.capture_status import capture_status, apply_capture_status
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import timestamp_utc_now

PRIMARY_KEY_NAME = 'id'
PRIMARY_KEY_TYPE = 'S'

@apply_capture_status
class Dynamo_DB__Table(Kwargs_To_Self):
    dynamo_db  : Dynamo_DB
    key_name   : str
    key_type   : str
    table_name : str


    def __init__(self, **kwargs):
        self.key_name = PRIMARY_KEY_NAME
        self.key_type = PRIMARY_KEY_TYPE
        super().__init__(**kwargs)

    def add_document(self, document):
        if self.key_name not in document:
            document[self.key_name] = self.dynamo_db.random_id()     # If key is present, generate a random UUID as the key
        return self.dynamo_db.document_add(table_name=self.table_name, key_name=self.key_name, document=document)

    def add_documents(self, documents):
        for document in documents:
            if self.key_name not in document:
                document[self.key_name] = str(uuid.uuid4())
        return self.dynamo_db.documents_add(table_name=self.table_name, documents=documents)

    def add_record(self, record : Dynamo_DB__Record):
        metadata = record.metadata
        metadata.timestamp_created = timestamp_utc_now()
        document   = record.serialize_to_dict()
        add_result = self.add_document(document)
        if add_result.get('status') == 'ok':
            return add_result.get('data')
        raise Exception(f'Error adding record: {add_result}')

    def create_table(self):
        return self.dynamo_db.table_create(table_name=self.table_name, key_name=self.key_name)

    def clear_table(self):
        return self.dynamo_db.documents_delete_all(table_name=self.table_name, key_name=self.key_name)

    def delete_document(self, key_value):
        return self.dynamo_db.document_delete(table_name=self.table_name, key_name=self.key_name, key_value=key_value)

    def delete_table(self, wait_for_deletion=True):
        return self.dynamo_db.table_delete(table_name=self.table_name, wait_for_deletion=wait_for_deletion)

    def document(self, key_value):
        return self.dynamo_db.document(table_name=self.table_name, key_name=self.key_name, key_value=key_value)

    def documents(self):
        return self.dynamo_db.documents_all(table_name=self.table_name)

    def exists(self):
        return self.dynamo_db.table_exists(table_name=self.table_name)

    def info(self):
        return self.dynamo_db.table_info(table_name=self.table_name)

    def keys(self):
        return self.dynamo_db.documents_keys(table_name=self.table_name, key_name=self.key_name, key_type=self.key_type)

    def query(self, **kwargs):
        return self.dynamo_db.client().query(**kwargs)          # todo: refactor this to add values that we know here (like TableName)

    def status(self):
        return self.dynamo_db.table_status(table_name=self.table_name)