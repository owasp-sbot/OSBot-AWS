from osbot_aws.aws.dynamo_db.Dynamo_DB__Table       import Dynamo_DB__Table

class DyDB__Table(Dynamo_DB__Table):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_document(self, document):
        result = super().add_document(document)
        if result.get('status') == 'ok':
            return result.get('data')
        return result

    def add_documents(self,documents):
        return super().add_documents(documents).get('data')

    def create_table_kwargs(self):
        key_schema               = [{'AttributeName': self.key_name  , 'KeyType'      : 'HASH'}]
        attribute_definitions    = [{'AttributeName': self.key_name  , 'AttributeType': 'S'   }]
        #global_secondary_indexes = []

        # for index in self.global_secondary_indexes:
        #     attribute_definitions   .append({ 'AttributeName': index, 'AttributeType': 'S' })
        #     global_secondary_indexes.append({ 'IndexName': f'{index}_index',
        #                                       'KeySchema': [{'AttributeName': index, 'KeyType': 'HASH'}],
        #                                       'Projection': {'ProjectionType': 'ALL'} })
        kwargs   = { 'AttributeDefinitions'  : attribute_definitions    ,
                     'BillingMode'           : 'PAY_PER_REQUEST'        ,
                     'KeySchema'             : key_schema               ,
                     #'GlobalSecondaryIndexes': global_secondary_indexes ,
                     'TableName'             : self.table_name           }
        return kwargs

    def create_table(self, wait_for_table=True):
        if not self.table_name:
            raise ValueError('Table name is required')
        if self.exists():
            return False

        kwargs = self.create_table_kwargs()
        self.dynamo_db.client().create_table(**kwargs)
        if wait_for_table:
            self.dynamo_db.wait_for('table_exists', self.table_name)
        return True

    def delete_document(self, document_id):
        result = super().delete_document(key_value=document_id)
        return result.get('status') == 'ok'

    def delete_documents(self, documents_ids):
        return super().delete_documents(keys_values=documents_ids).get('data')

    def delete_table(self, wait_for_deletion=False):
        return super().delete_table(wait_for_deletion=wait_for_deletion).get('data')

    def document(self, document_id):
        return super().document(key_value=document_id).get('data')

    def document_exists(self, document_id):
        return self.document(document_id) != {}

    def documents(self, documents_ids):
        return super().documents(keys_values=documents_ids).get('data').get('all_responses')

    def documents_all(self, **kwargs):
        return super().documents_all().get('data')

    def documents_ids(self, **kwargs):
        return super().documents_ids(**kwargs).get('data')

    def dydb_document(self, document_id, load_data=True):
        from osbot_aws.aws.dynamo_db.models.DyDB__Document import DyDB__Document        # need to import this here due to circular references
        document = None                                                                 # create var to hold document data
        if load_data:                                                                   # if asked to load data
            document = self.document(document_id)                                       # try to load data (this will return None if the document doesn't exist)
        if not document:                                                                # if load_data is False or self.document(document_id) returned none
            document = {self.key_name: document_id}                                     # create a default document representation with only the id
        kwargs_document = dict(document = document,                                     # kwargs for DyDB__Document object
                               table    = self    )                                     #     where pass a reference to the current table
        return DyDB__Document(**kwargs_document)                                        # create DyDB__Document

    def exists(self):
        return super().exists().get('data')

    def info(self):
        return super().info().get('data')

    def not_exists(self):
        return self.exists() is False

    def size(self):
        return self.dynamo_db.documents_count(self.table_name)

    def query_index(self, index_name, index_type, index_value):
            query_kwargs = dict( TableName                 = self.table_name                                ,
                                 IndexName                 = index_name                                     ,
                                 KeyConditionExpression    =  f'#{index_name} = :{index_name}'              ,
                                 ExpressionAttributeNames  = { f'#{index_name}' : index_name                },
                                 ExpressionAttributeValues = { f':{index_name}' : {index_type :index_value  }})
            response = self.query(**query_kwargs)

            items = response.get('data', {}).get('Items', [])           # todo: add cases with large results
            return [self.dynamo_db.document_deserialize(item) for item in items]

    def query_index_between_range(self, index_name, index_type, index_value, sort_key, sort_key_type, start_value, end_value, query_filter=None):
        from osbot_utils.utils.Misc import list_set

        query_kwargs = dict( TableName                 = self.table_name                        ,
                             IndexName                 = index_name                 ,
                             KeyConditionExpression    =  f'#{index_name} = :{index_name} AND #{sort_key} BETWEEN :start AND :end',
                             ExpressionAttributeNames  = { f'#{index_name}' : index_name,   f'#{sort_key}': sort_key }            ,
                             ExpressionAttributeValues = { f':{index_name}' : {index_type :index_value    },
                                                           ':start'         : { sort_key_type : str(start_value)},
                                                           ':end'           : { sort_key_type : str(end_value  )}})
        if query_filter and list_set(query_filter) == ['expression_attr_names', 'expression_attr_values', 'filter_expression']:
            query_kwargs['ExpressionAttributeNames' ].update(query_filter.get('expression_attr_names'))
            query_kwargs['ExpressionAttributeValues'].update(query_filter.get('expression_attr_values'))
            query_kwargs['FilterExpression'         ] = query_filter.get('filter_expression')

        #pprint(query_kwargs)
        response = self.query(**query_kwargs)

        items = response.get('data', {}).get('Items', [])           # todo: add cases with large results
        return [self.dynamo_db.document_deserialize(item) for item in items]