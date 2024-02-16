from functools import cache

from   boto3    import resource
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

from osbot_aws.apis.Session import Session
from osbot_utils.decorators.methods.remove_return_value import remove_return_value


class Dynamo_DB:
    def __init__(self):
        pass
        #self.resource   = resource('dynamodb')
        # self._dynamo    = None
        # self._streams   = None

    def __enter__(self                           ): return self
    def __exit__ (self, exc_type, exc_val, exc_tb): pass

    # helpers
    @cache
    def client(self):
        return Session().client('dynamodb')

    @cache
    def client__dynamo_streams(self):
        return Session().client('dynamodbstreams')

    # main methods

    def document(self, table_name, key_name, key_value):
        key    = {key_name: {'S': key_value}}
        result = self.client().get_item(TableName=table_name, Key=key)
        item   = result.get('Item')
        return self.document_deserialise(item)

    def document_add(self, table_name, document):
        document_as_item = self.document_serialise(document)

        self.client().put_item(TableName=table_name, Item=document_as_item)
        return self

    def document_delete(self, table_name, key_name, key_value):
        key = { key_name: {'S': key_value} }
        self.client().delete_item( TableName=table_name, Key=key )
        return True

    def document_deserialise(self, item):
        if item:
            deserializer = TypeDeserializer()
            return {k: deserializer.deserialize(v) for k, v in item.items()}
        return {}

    def document_serialise(self, document):
        serializer = TypeSerializer()
        return {k: serializer.serialize(v) for k, v in document.items()}

    def documents_add(self, table_name, documents):
        try:
            chunks = [documents[x:x + 25] for x in range(0, len(documents), 25)]        # Split the items list into chunks of 25 (DynamoDB batch write limit)
            responses = []

            for chunk in chunks:
                request_items = { table_name: [ {'PutRequest': {'Item': self.document_serialise(document)}}
                                                  for document in chunk ] }
                response = self.client().batch_write_item(RequestItems=request_items)
                del response['ResponseMetadata']
                responses.append(response)
            return responses        # Contains unprocessed items
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

    def documents_all(self, table_name):
        """
        Retrieves all items from the DynamoDB table.
        :return: A list of dictionaries, each representing an item in the table.
        """
        try:
            response = self.client().scan(TableName=table_name)
            items    = response.get('Items', [])
            return [self.document_deserialise(item) for item in items]
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return []

    def documents_delete(self, table_name, key_name, key_values):
        try:
            keys = [{key_name: {'S': key_value}} for key_value in key_values]

            chunks = [keys[x:x+25] for x in range(0, len(keys), 25)]        # Split the keys list into chunks of 25 (DynamoDB batch write limit)
            responses = []

            for chunk in chunks:
                request_items = { table_name: [{'DeleteRequest': {'Key': key}} for key in chunk ] }
                response = self.client().batch_write_item(RequestItems=request_items)
                del response['ResponseMetadata']
                responses.append(response)

            return responses
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

    def documents_keys(self, table_name, key_name):
        """
        Retrieves only the key attributes for all items in the DynamoDB table.
        :param table_name: Name of the DynamoDB table.
        :param key_name: The name of the primary key attribute.
        :return: A list of key values for all items in the table.
        """
        try:
            response = self.client().scan(TableName=table_name, ProjectionExpression=key_name)
            items    = response.get('Items', [])
            return [item[key_name]['S'] for item in items]
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return []


    def table_create(self, table_name, key_name, with_streams=False):
        if self.table_exists(table_name):
            return False
        keySchema             = [{'AttributeName'    : key_name        , 'KeyType'           : 'HASH'}]
        attributeDefinitions  = [{'AttributeName'    : key_name        , 'AttributeType'     : 'S'}]
        provisionedThroughput = { 'ReadCapacityUnits' : 5          , 'WriteCapacityUnits': 5      }
        kwargs   = { 'TableName'            : table_name           ,
                     'KeySchema'            : keySchema            ,
                     'AttributeDefinitions' : attributeDefinitions ,
                     'ProvisionedThroughput': provisionedThroughput }
        if with_streams:
            kwargs['StreamSpecification'] = {'StreamEnabled': True, 'StreamViewType': 'NEW_IMAGE' }
        self.client().create_table(**kwargs)

        self.client().get_waiter('table_exists') \
            .wait(TableName=table_name, WaiterConfig={'Delay': 1, 'MaxAttempts': 50})
        return True

    def table_delete(self, table_name, wait_for_deletion=True):
        if self.table_exists(table_name) is False:
            return False
        self.client().delete_table(TableName = table_name)
        if wait_for_deletion:
            self.client().get_waiter('table_not_exists')      \
                       .wait(TableName=table_name, WaiterConfig={'Delay': 5, 'MaxAttempts':20 })
        return True

    def table_exists(self, table_name):
        return self.table_info(table_name) != {}

    def table_info(self, table_name):
        try:
            return self.client().describe_table(TableName=table_name).get('Table')
        except:
            return {}

    def table_status(self, table_name):
        return self.table_info(table_name).get('TableStatus')

    def tables(self):
        result = self.client().list_tables() or {}
        return result.get('TableNames') or []

    def streams(self):
        return self.client__dynamo_streams().list_streams().get('Streams')
