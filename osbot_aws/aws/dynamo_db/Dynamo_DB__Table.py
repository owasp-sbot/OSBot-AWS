import uuid

from osbot_aws.aws.dynamo_db.Dynamo_DB import Dynamo_DB
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.decorators.methods.capture_status import capture_status, apply_capture_status
from osbot_utils.utils.Dev import pprint


@apply_capture_status
class Dynamo_DB__Table(Kwargs_To_Self):
    dynamo_db  : Dynamo_DB
    key_name   : str
    table_name : str


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_document(self, document):
        if self.key_name not in document:
            document[self.key_name] = str(uuid.uuid4())     # If key is present, generate a random UUID as the key
        return self.dynamo_db.document_add(table_name=self.table_name, key_name=self.key_name, document=document)

    def create_table(self):
        return self.dynamo_db.table_create(table_name=self.table_name, key_name=self.key_name)

    def clear_table(self):
        return self.dynamo_db.documents_delete_all(table_name=self.table_name, key_name=self.key_name)

    def delete_document(self, key_value):
        return self.dynamo_db.document_delete(table_name=self.table_name, key_name=self.key_name, key_value=key_value)

    def delete_table(self):
        return self.dynamo_db.table_delete(table_name=self.table_name)

    def documents(self):
        return self.dynamo_db.documents_all(table_name=self.table_name)

    def exists(self):
        return self.dynamo_db.table_exists(table_name=self.table_name)

    def info(self):
        return self.dynamo_db.table_info(table_name=self.table_name)

    def keys(self):
        return self.dynamo_db.documents_keys(table_name=self.table_name, key_name=self.key_name)

    def status(self):
        return self.dynamo_db.table_status(table_name=self.table_name)