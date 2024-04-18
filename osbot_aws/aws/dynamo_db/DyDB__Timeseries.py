from os import environ

from osbot_aws.aws.dynamo_db.Dynamo_DB__Table   import Dynamo_DB__Table
from osbot_utils.utils.Misc                     import timestamp_utc_now
from osbot_utils.utils.Objects import type_full_name

NAME_TIMESTAMP   = 'timestamp'
NAME_ENVIRONMENT = 'environment'
NAME_DATA        = 'data'
VALUE_NA         = 'NA'
class DyDB__Timeseries(Dynamo_DB__Table):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.table_name          = 'tcb_timeseries'
        #self.key_name
        #self.primary_key         = 'dy_id'
        #self.key_name            = 'timestamp'
        #self.key_attribute_type  = 'N'
        self.key_type            = 'RANGE'
        self.index_name          = 'timestamp_index'
        #self.partition_key_name  = 'partition_key'     # use env instead of partition
        #self.partition_key_value = 'PROD'
        #self.data_field_name     = 'data'
        self.global_secondary_indexes = []

    def add_document(self, document, env=None):
        if NAME_ENVIRONMENT not in document:
            document[NAME_ENVIRONMENT] = environ.get('EXECUTION_ENV') or VALUE_NA
        if NAME_TIMESTAMP not in document:
            document[NAME_TIMESTAMP] = timestamp_utc_now()
        result = super().add_document(document)
        return result

    def all_ids(self):                                                                          # todo: see if this can be moved to Dynamo_DB__Table
        response = self.dynamo_db.client().scan(TableName            = self.table_name ,
                                                ProjectionExpression = self.key_name   )
        ids = []
        for item in response.get('Items'):
            ids.append(item.get(self.key_name).get('S'))
        return ids

    def clear_table(self):                                                                      # todo: see if this can be moved to Dynamo_DB__Table
        table_name = self.table_name
        key_name   = self.key_name
        key_values = self.all_ids()
        delete_result = self.dynamo_db.documents_delete(table_name=table_name, key_name=key_name, key_values=key_values)
        return delete_result

    def create_kwargs(self):
        #primary_key        = self.primary_key
        table_name         = self.table_name
        #key_attribute_type = self.key_attribute_type
        key_type           = self.key_type
        index_name         = self.index_name

        if self.dynamo_db.table_exists(table_name):
            return False

        key_schema               = [{'AttributeName': self.key_name  , 'KeyType'      : 'HASH'}]
        attribute_definitions    = [{'AttributeName': self.key_name  , 'AttributeType': 'S'   },
                                    {'AttributeName': NAME_TIMESTAMP , 'AttributeType': 'N'   }]
        global_secondary_indexes = [{ 'IndexName' : index_name,
                                      'KeySchema' : [ {'AttributeName' :NAME_TIMESTAMP, 'KeyType': 'HASH'  },
                                                      { 'AttributeName': self.key_name  , 'KeyType': key_type}],
                                      'Projection': {'ProjectionType': 'ALL'} }]

        for index in self.global_secondary_indexes:
            attribute_definitions   .append({ 'AttributeName': index, 'AttributeType': 'S' })
            global_secondary_indexes.append({ 'IndexName': f'{index}_index',
                                              'KeySchema': [{'AttributeName': index, 'KeyType': 'HASH'}],
                                              'Projection': {'ProjectionType': 'ALL'} })
        kwargs   = { 'AttributeDefinitions'  : attribute_definitions    ,
                     'BillingMode'           : 'PAY_PER_REQUEST'        ,
                     'KeySchema'             : key_schema               ,
                     'GlobalSecondaryIndexes': global_secondary_indexes ,
                     'TableName'             : table_name               }
        return kwargs

    def create_table(self):
        kwargs = self.create_kwargs()
        self.dynamo_db.client().create_table(**kwargs)

        self.dynamo_db.client().get_waiter('table_exists') \
            .wait(TableName=self.table_name, WaiterConfig={'Delay': 1, 'MaxAttempts': 50})
        return True

    def delete_document(self, key_value):
        return self.dynamo_db.document_delete(table_name=self.table_name, key_name=self.key_name, key_value=key_value)

    def document(self, key_value):
        return self.dynamo_db.document(table_name=self.table_name, key_name=self.primary_key, key_value=key_value)

    def documents(self, partition=None):
        return self.query_by_partition(partition or self.partition_key_value)

    def query_by_partition(self, partition_value):
        table_name              = self.table_name
        index_name              = self.index_name
        partition_key_name      = self.partition_key_name
        primary_key_placeholder = "#pk"

        kwargs = dict(TableName                 = table_name,
                      IndexName                 = index_name,
                      KeyConditionExpression    = f'{primary_key_placeholder} = :value' ,
                      ExpressionAttributeNames  = { primary_key_placeholder: partition_key_name},
                      ExpressionAttributeValues = { ':value': {'S': partition_value  }})
        result = self.query(**kwargs)
        items  = []
        if result:
            for raw_item in result.get('data').get('Items'):
                item = self.dynamo_db.document_deserialise(raw_item)
                items.append(item)
        return items

    def query_by_last_n_hours(self, hours, partition=None):
        start_timestamp = timestamp_utc_now() - (hours * 60 * 60 * 1000)
        end_timestamp   = timestamp_utc_now()
        return self.query_by_timestamp(start_timestamp, end_timestamp, partition=partition)

    def query_by_timestamp(self, start_timestamp, end_timestamp, partition=None):
        if partition == 'None':
            partition = self.partition_key_value
        table_name              = self.table_name
        index_name              = self.index_name
        key_name                = self.key_name
        partition_key_name      = self.partition_key_name
        partition_key_value     = partition or self.partition_key_value
        primary_key_placeholder = "#pk"
        sort_key_placeholder    = "#sk"

        kwargs = dict(TableName                 = table_name,
                      IndexName                 = index_name,
                      KeyConditionExpression    = f'{primary_key_placeholder} = :value AND {sort_key_placeholder} BETWEEN :start AND :end',
                      ExpressionAttributeNames  = { sort_key_placeholder   : key_name          ,
                                                    primary_key_placeholder: partition_key_name},
                      ExpressionAttributeValues = { ':value': {'S': partition_key_value  },
                                                    ':start': {'N': str(start_timestamp) },
                                                    ':end'  : {'N': str(end_timestamp  ) }})
        result = self.query(**kwargs)
        items  = []
        for raw_item in result.get('data', {}).get('Items',[]):
            item = self.dynamo_db.document_deserialise(raw_item)
            items.append(item)
        return items

    def query_by_primary_key(self, key_value):
        table_name                  = self.table_name
        dynamodb_client             = self.dynamo_db.client()
        key_condition_expression    = '#primary_key_name = :primary_key_value'
        expression_attribute_names  = { '#primary_key_name': self.primary_key }
        expression_attribute_values = { ':primary_key_value': {'S': key_value} }
        result = dynamodb_client.query( TableName                 = table_name                  ,
                                        KeyConditionExpression    = key_condition_expression    ,
                                        ExpressionAttributeNames  = expression_attribute_names  ,
                                        ExpressionAttributeValues = expression_attribute_values )

        items = result.get('Items', [])
        return self.dynamo_db.document_deserialise(items[0]) if items else {}