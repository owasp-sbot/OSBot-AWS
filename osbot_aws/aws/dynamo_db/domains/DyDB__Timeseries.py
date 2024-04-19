# todo: refactor code to use DyDB__Table_With_Timestamp which has improved support for using timestamps in DyDB tables
# from os import environ
#
# from osbot_aws.aws.dynamo_db.Dynamo_DB__Table   import Dynamo_DB__Table
# from osbot_aws.aws.dynamo_db.domains.DyDB__Table import DyDB__Table
# from osbot_utils.utils.Misc                     import timestamp_utc_now
# from osbot_utils.utils.Objects import type_full_name
#
# NAME_TIMESTAMP   = 'timestamp'
# NAME_ENVIRONMENT = 'environment'
# NAME_DATA        = 'data'
# VALUE_NA         = 'NA'
#
# class DyDB__Timeseries(DyDB__Table):
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.global_secondary_indexes = []
#
#     def add_document(self, document, env=None):
#         if NAME_ENVIRONMENT not in document:
#             document[NAME_ENVIRONMENT] = environ.get('EXECUTION_ENV') or VALUE_NA
#         if NAME_TIMESTAMP not in document:
#             document[NAME_TIMESTAMP] = timestamp_utc_now()
#         result = super().add_document(document)
#         return result
#
#     def all_ids(self):                                                                          # todo: see if this can be moved to Dynamo_DB__Table
#         response = self.dynamo_db.client().scan(TableName            = self.table_name ,
#                                                 ProjectionExpression = self.key_name   )
#         ids = []
#         for item in response.get('Items'):
#             ids.append(item.get(self.key_name).get('S'))
#         return ids
#
#     def clear_table(self):                                                                      # todo: see if this can be moved to Dynamo_DB__Table
#         table_name  = self.table_name
#         key_name    = self.key_name
#         keys_values = self.all_ids()
#         delete_result = self.dynamo_db.documents_delete(table_name=table_name, key_name=key_name, keys_values=keys_values)
#         return delete_result
#
#     def query_by_partition(self, partition_value):
#         table_name              = self.table_name
#         index_name              = self.index_name
#         partition_key_name      = self.partition_key_name
#         primary_key_placeholder = "#pk"
#
#         kwargs = dict(TableName                 = table_name,
#                       IndexName                 = index_name,
#                       KeyConditionExpression    = f'{primary_key_placeholder} = :value' ,
#                       ExpressionAttributeNames  = { primary_key_placeholder: partition_key_name},
#                       ExpressionAttributeValues = { ':value': {'S': partition_value  }})
#         result = self.query(**kwargs)
#         items  = []
#         if result:
#             for raw_item in result.get('data').get('Items'):
#                 item = self.dynamo_db.document_deserialise(raw_item)
#                 items.append(item)
#         return items
#
#     def query_by_last_n_hours(self, hours, partition=None):
#         start_timestamp = timestamp_utc_now() - (hours * 60 * 60 * 1000)
#         end_timestamp   = timestamp_utc_now()
#         return self.query_by_timestamp(start_timestamp, end_timestamp, partition=partition)
#
#     def query_by_timestamp(self, start_timestamp, end_timestamp, partition=None):
#         if partition == 'None':
#             partition = self.partition_key_value
#         table_name              = self.table_name
#         index_name              = self.index_name
#         key_name                = self.key_name
#         partition_key_name      = self.partition_key_name
#         partition_key_value     = partition or self.partition_key_value
#         primary_key_placeholder = "#pk"
#         sort_key_placeholder    = "#sk"
#
#         kwargs = dict(TableName                 = table_name,
#                       IndexName                 = index_name,
#                       KeyConditionExpression    = f'{primary_key_placeholder} = :value AND {sort_key_placeholder} BETWEEN :start AND :end',
#                       ExpressionAttributeNames  = { sort_key_placeholder   : key_name          ,
#                                                     primary_key_placeholder: partition_key_name},
#                       ExpressionAttributeValues = { ':value': {'S': partition_key_value  },
#                                                     ':start': {'N': str(start_timestamp) },
#                                                     ':end'  : {'N': str(end_timestamp  ) }})
#         result = self.query(**kwargs)
#         items  = []
#         for raw_item in result.get('data', {}).get('Items',[]):
#             item = self.dynamo_db.document_deserialise(raw_item)
#             items.append(item)
#         return items
#
#     def query_by_primary_key(self, key_value):
#         table_name                  = self.table_name
#         dynamodb_client             = self.dynamo_db.client()
#         key_condition_expression    = '#primary_key_name = :primary_key_value'
#         expression_attribute_names  = { '#primary_key_name': self.primary_key }
#         expression_attribute_values = { ':primary_key_value': {'S': key_value} }
#         result = dynamodb_client.query( TableName                 = table_name                  ,
#                                         KeyConditionExpression    = key_condition_expression    ,
#                                         ExpressionAttributeNames  = expression_attribute_names  ,
#                                         ExpressionAttributeValues = expression_attribute_values )
#
#         items = result.get('Items', [])
#         return self.dynamo_db.document_deserialise(items[0]) if items else {}