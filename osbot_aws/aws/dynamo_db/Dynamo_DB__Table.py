from osbot_aws.aws.dynamo_db.Dynamo_DB import Dynamo_DB
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self


class Dynamo_DB__Table(Kwargs_To_Self):
    dynamo_db  : Dynamo_DB
    key_name   : str
    table_name : str


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create(self):
        return self.dynamo_db.table_create(table_name=self.table_name, key_name=self.key_name)

    def delete(self):
        return self.dynamo_db.table_delete(table_name=self.table_name)

    def exists(self):
        return self.info() != {}

    def info(self):
        return self.dynamo_db.table_info(table_name=self.table_name)