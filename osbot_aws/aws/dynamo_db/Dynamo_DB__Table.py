from osbot_utils.base_classes.Type_Safe                 import Type_Safe
from osbot_aws.aws.dynamo_db.Dynamo_DB                  import Dynamo_DB
from osbot_utils.decorators.methods.capture_status      import apply_capture_status


PRIMARY_KEY_NAME = 'id'
PRIMARY_KEY_TYPE = 'S'

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from osbot_aws.aws.dynamo_db.Dynamo_DB__Record          import Dynamo_DB__Record

@apply_capture_status
class Dynamo_DB__Table(Type_Safe):
    dynamo_db  : Dynamo_DB
    key_name   : str
    key_type   : str
    table_name : str

    def __init__(self, **kwargs):
        self.key_name = PRIMARY_KEY_NAME
        self.key_type = PRIMARY_KEY_TYPE
        super().__init__(**kwargs)

    def add_document(self, document):
        key_value = document.get(self.key_name)
        if not key_value:                                                   # if key value is not set
            document = {**document ,                                        # to the current document object
                        self.key_name : self.dynamo_db.random_id()}         # add it as a random UUID
        return self.dynamo_db.document_add(table_name=self.table_name, document=document)

    def add_documents(self, documents):
        documents_to_add = []
        for document in documents:
            if self.key_name not in document:                               # If key is present,
                document = {self.key_name: self.dynamo_db.random_id(),      # add random UUID as the key
                            **document}                                     # to the current document object
            documents_to_add.append(document)
        return self.dynamo_db.documents_add(table_name=self.table_name, documents=documents_to_add)

    def add_record(self, record : 'Dynamo_DB__Record'):
        from osbot_utils.utils.Misc import timestamp_utc_now
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

    def delete_documents(self, keys_values):
        return self.dynamo_db.documents_delete(table_name=self.table_name, key_name=self.key_name, keys_values=keys_values)

    def delete_table(self, wait_for_deletion=True):
        return self.dynamo_db.table_delete(table_name=self.table_name, wait_for_deletion=wait_for_deletion)

    def document(self, key_value):
        return self.dynamo_db.document(table_name=self.table_name, key_name=self.key_name, key_value=key_value)

    def documents(self, keys_values):
        return self.dynamo_db.documents(table_name=self.table_name, key_name=self.key_name, keys_values=keys_values)

    def documents_all(self):
        return self.dynamo_db.documents_all(table_name=self.table_name)

    def documents_ids(self,**kwargs):
        return self.dynamo_db.documents_ids(table_name=self.table_name, key_name=self.key_name, **kwargs)

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

    def update_table(self, attribute_definitions=None, gsi_updates=None):
        return self.dynamo_db.table_update(self.table_name, attribute_definitions=attribute_definitions, gsi_updates=gsi_updates)

    def gsi_create(self, partition_name, partition_type, sort_key=None, sort_key_type=None, sort_key_schema=None, projection_type='ALL'):
        gsi_create_kwargs= self.gsi_create_kwargs( partition_name  = partition_name    ,
                                                   partition_type  = partition_type    ,
                                                   sort_key        = sort_key          ,
                                                   sort_key_type   = sort_key_type     ,
                                                   sort_key_schema = sort_key_schema   ,
                                                   projection_type = projection_type   ).get('data')
        return self.gsi_create_index(**gsi_create_kwargs).get('data')               # todo: add check for status =='ok'

    def gsi_create_index(self, attribute_definitions, gsi_update):
        gsi_updates = [gsi_update]
        return self.gsi_create_indexes(attribute_definitions, gsi_updates)

    def gsi_create_indexes(self, attribute_definitions, gsi_updates):
        result = self.update_table( attribute_definitions=attribute_definitions, gsi_updates=gsi_updates)
        if result.get('status') == 'ok':
            return result.get('data')
        return result

    def gsi_create_kwargs(self, partition_name, partition_type, sort_key=None, sort_key_type=None, sort_key_schema=None, projection_type='ALL'):
        attribute_definitions = [{ 'AttributeName': partition_name,
                                   'AttributeType': partition_type}]
        gsi_update            = {'Create': { 'IndexName' : partition_name                        ,
                                             'KeySchema' : [{ 'AttributeName' : partition_name   ,
                                                              'KeyType'       : 'HASH'           }],
                                             'Projection':  { 'ProjectionType': projection_type  }}}
        if sort_key and sort_key_type and sort_key_schema:
            attribute_definitions.append({ 'AttributeName': sort_key,
                                           'AttributeType': sort_key_type})
            gsi_update.get('Create').get('KeySchema').append({ 'AttributeName' : sort_key           ,
                                                               'KeyType'       : sort_key_schema })
        create_kwargs = dict(attribute_definitions = attribute_definitions,
                             gsi_update            = gsi_update)
        return create_kwargs

    def gsi_delete(self, index_name):
        gsi_update  = {'Delete': { 'IndexName' : index_name }}
        gsi_updates = [gsi_update]
        return self.update_table(gsi_updates=gsi_updates).get('data')

    def gsi_wait_for_status(self, status='ACTIVE', max_attempts=20, delay=0.05):        # todo: see if these values need to be higher when dealing with AWS DynamoDB (vs the dynamodb-local)
        from osbot_utils.utils.Misc import wait_for

        for i in range(max_attempts):
            all_match = False
            for gsi in self.gsis().get('data'):
                if gsi.get('IndexStatus') == status:
                    all_match = True
                else:
                    all_match = False
                    break

            if all_match:
                return True
            else:
                wait_for(delay)
        raise ValueError("expected status not found")


    def gsis(self):
        return self.info().get('GlobalSecondaryIndexes')