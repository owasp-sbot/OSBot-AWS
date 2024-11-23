from osbot_utils.base_classes.Type_Safe                 import Type_Safe
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from osbot_utils.decorators.methods.remove_return_value import remove_return_value

DEFAULT_DOCUMENTS_MAX_ITEMS_TO_FETCH = 100000
DEFAULT_DOCUMENTS_FETCH_BATCH_SIZE   = 20000

class Dynamo_DB(Type_Safe):
    region_name : str = None
    endpoint_url: str = None
    # def __enter__(self                           ): return self
    # def __exit__ (self, exc_type, exc_val, exc_tb): pass

    # helpers
    @cache_on_self
    def client(self):
        from osbot_aws.apis.Session import Session

        return Session().client(service_name='dynamodb', region_name=self.region_name, endpoint_url=self.endpoint_url)

    @cache_on_self
    def client__dynamo_streams(self):
        from osbot_aws.apis.Session import Session

        return Session().client('dynamodbstreams')

    # main methods

    def document(self, table_name, key_name, key_value):
        key    = {key_name: {'S': key_value}}
        result = self.client().get_item(TableName=table_name, Key=key)
        item   = result.get('Item')
        return self.document_deserialize(item)

    def document_add(self, table_name, document):
        document_as_item = self.document_serialize(document)
        self.client().put_item(TableName=table_name, Item=document_as_item)
        result = dict(document=document, document_as_item=document_as_item)
        return result

    def document_delete(self, table_name, key_name, key_value):
        key = { key_name: {'S': key_value} }
        self.client().delete_item( TableName=table_name, Key=key ) # note: there is no clue from DynamoDB if it worked or not
        return True                                                #       so unless there was an exception thrown, assume it did

    def document_deserialize(self, item):
        from boto3.dynamodb.types import TypeDeserializer
        if item:
            deserializer = TypeDeserializer()
            return {k: deserializer.deserialize(v) for k, v in item.items()}
        return {}

    @remove_return_value('ResponseMetadata')
    def document_update(self, table_name, key_name, key_value, update_data):
        from boto3.dynamodb.types import TypeSerializer

        # Initialize TypeSerializer to convert Python types to DynamoDB types
        serializer = TypeSerializer()

        # Construct the key for the item to update
        key = {key_name: {'S': key_value}}

        # Initialize the update expression components
        update_expression = "SET "
        expression_attribute_values = {}
        expression_attribute_names = {}

        for attribute_name, new_value in update_data.items():
            # Serialize the value to DynamoDB format
            dynamodb_value = serializer.serialize(new_value)

            # Create placeholders for attribute names and values
            attr_placeholder = f"#{attribute_name.replace('-', '_')}"
            val_placeholder = f":val_{attribute_name.replace('-', '_')}"

            # Add to the update expression, attribute names, and values
            update_expression += f"{attr_placeholder} = {val_placeholder}, "
            expression_attribute_names[attr_placeholder] = attribute_name
            expression_attribute_values[val_placeholder] = dynamodb_value

        # Remove the trailing comma and space from the update expression
        update_expression = update_expression.rstrip(', ')

        # Perform the update operation
        response = self.client().update_item(
            TableName=table_name,
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW"
        )
        return response

    def document_serialize(self, document):
        from boto3.dynamodb.types import TypeSerializer

        serializer = TypeSerializer()
        return {k: serializer.serialize(v) for k, v in document.items()}

    def documents_add(self, table_name, documents):
        chunks = [documents[x:x + 25] for x in range(0, len(documents), 25)]        # Split the items list into chunks of 25 (DynamoDB batch write limit)
        responses = []

        for chunk in chunks:
            request_items = { table_name: [ {'PutRequest': {'Item': self.document_serialize(document)}}
                                              for document in chunk ] }
            response = self.client().batch_write_item(RequestItems=request_items)
            del response['ResponseMetadata']
            responses.append(response)
        result = dict(documents=documents, responses=responses)
        return result                                               # Contains unprocessed items

    def documents(self, table_name, key_name, keys_values):
        keys = []
        for key_value in keys_values:
            key = {key_name: {'S': key_value}}
            keys.append(key)

        chunks = [keys[x:x + 100] for x in range(0, len(keys), 100)]  # Split the items list into chunks of 100 (DynamoDB batch_get_item limit)

        all_responses        = []
        all_responses_raw    = []
        all_unprocessed_keys = []
        for chunk in chunks:
            kwargs           = {'RequestItems': {table_name: {'Keys': chunk}}}
            result           = self.client().batch_get_item(**kwargs)
            responses        = result.get('Responses')
            unprocessed_keys = result.get('UnprocessedKeys')
            all_responses_raw   .extend(responses.get(table_name))
            all_unprocessed_keys.append(unprocessed_keys)
        for response_raw in all_responses_raw:
            response = self.document_deserialize(response_raw)
            all_responses.append(response)

        return dict(all_responses        = all_responses        ,
                    all_unprocessed_keys = all_unprocessed_keys )

    def documents_all(self, table_name, batch_size=DEFAULT_DOCUMENTS_FETCH_BATCH_SIZE, max_fetch=DEFAULT_DOCUMENTS_MAX_ITEMS_TO_FETCH):
        #todo: figure out why this is only returning 64 records at the time
        items = []
        last_evaluated_key = None

        while True:
            scan_kwargs = {
                'TableName': table_name,
                'Limit'    : batch_size   # Specify the limit here
            }
            if last_evaluated_key:
                scan_kwargs['ExclusiveStartKey'] = last_evaluated_key

            response = self.client().scan(**scan_kwargs)
            items.extend(response.get('Items', []))
            last_evaluated_key = response.get('LastEvaluatedKey')

            if not last_evaluated_key:
                break
            if len(items) > max_fetch:
                break

        return [self.document_deserialize(item) for item in items]

    # todo:  figure out why code below returns only 64
    def documents_count(self, table_name):
        count_total  = 0
        response     = self.client().scan(TableName=table_name, Select='COUNT')
        count_total += response.get('Count', 0)
        while 'LastEvaluatedKey' in response:
            response = self.client().scan(TableName=table_name, Select='COUNT', ExclusiveStartKey=response['LastEvaluatedKey'])
            count_total += response.get('Count', 0)
        return count_total

    def documents_delete(self, table_name, key_name, keys_values):

        keys = [{key_name: {'S': key_value}} for key_value in keys_values]

        chunks = [keys[x:x+25] for x in range(0, len(keys), 25)]        # Split the keys list into chunks of 25 (DynamoDB batch write limit)
        responses = []

        for chunk in chunks:
            request_items = { table_name: [{'DeleteRequest': {'Key': key}} for key in chunk ] }
            response = self.client().batch_write_item(RequestItems=request_items)
            del response['ResponseMetadata']
            responses.append(response)

        return responses

    def documents_delete_all(self, table_name, key_name):
        all_keys      = self.documents_keys  (table_name=table_name, key_name=key_name)
        delete_result = self.documents_delete(table_name=table_name, key_name=key_name, keys_values=all_keys)
        delete_status = True
        for response in delete_result:
            if response.get('UnprocessedItems'):
                delete_status = False
                break
        return dict(deleted_keys=all_keys, delete_result=delete_result, delete_status=delete_status)

    def documents_ids(self, table_name, key_name, batch_size=DEFAULT_DOCUMENTS_FETCH_BATCH_SIZE, max_fetch=DEFAULT_DOCUMENTS_MAX_ITEMS_TO_FETCH):

        scan_kwargs = dict(ProjectionExpression = key_name  ,
                           Limit                = batch_size,
                           TableName            = table_name)
        response = self.client().scan(**scan_kwargs)

        all_items = []
        all_items.extend(response['Items'])
        while 'LastEvaluatedKey' in response and len(all_items) < max_fetch:
            scan_kwargs['ExclusiveStartKey'] = response.get('LastEvaluatedKey')
            response = self.client().scan(**scan_kwargs)
            all_items.extend(response['Items'])

        ids = []
        for item in all_items:
            ids.append(item.get(key_name).get('S'))
        return ids

    def documents_keys(self, table_name, key_name, key_type='S'):
        """
        Retrieves only the key attributes for all items in the DynamoDB table.
        :param table_name: Name of the DynamoDB table.
        :param key_name: The name of the primary key attribute.
        :return: A list of key values for all items in the table.
        """
        #response = self.client().scan(TableName=table_name, ProjectionExpression=key_name)
        #items    = response.get('Items', [])
        response = self.client().scan(TableName                = table_name      , # target table
                                      ProjectionExpression     = '#k'            , # Use a placeholder in the expression
                                      ExpressionAttributeNames = {'#k': key_name}) # Define the placeholder
        items = response.get('Items', [])
        return [item[key_name][key_type] for item in items]


    def table_create(self, table_name, key_name, with_streams=False):
        if self.table_exists(table_name):
            return False
        keySchema             = [{'AttributeName'    : key_name        , 'KeyType'           : 'HASH'}]
        attributeDefinitions  = [{'AttributeName'    : key_name        , 'AttributeType'     : 'S'}]
        #provisionedThroughput = { 'ReadCapacityUnits' : 5          , 'WriteCapacityUnits': 5      }
        kwargs   = { 'TableName'            : table_name           ,
                     'KeySchema'            : keySchema            ,
                     'AttributeDefinitions' : attributeDefinitions ,
                     'BillingMode'          : 'PAY_PER_REQUEST'    }
                     #'ProvisionedThroughput': provisionedThroughput }      # todo: add support for handling provisioned throughput
        if with_streams:
            kwargs['StreamSpecification'] = {'StreamEnabled': True, 'StreamViewType': 'NEW_IMAGE' }
        self.client().create_table(**kwargs)

        self.wait_for(waiter_name='table_exists', table_name=table_name)
        return True

    def wait_for(self, waiter_name, table_name, delay=1, max_attempts= 50):
        kwargs = dict(TableName    = table_name,
                      WaiterConfig = dict(Delay=delay, MaxAttempts=max_attempts))
        self.client().get_waiter(waiter_name).wait(**kwargs)

    def wait_for_table_exists(self, table_name):
        self.wait_for(waiter_name='table_exists', table_name=table_name)

    def table_delete(self, table_name, wait_for_deletion=True):
        if self.table_exists(table_name) is False:
            return False
        self.client().delete_table(TableName = table_name)
        if wait_for_deletion:
            self.wait_for(waiter_name='table_not_exists', table_name=table_name)
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

    @remove_return_value(field_name='ResponseMetadata')
    def table_update(self, table_name, attribute_definitions=None, gsi_updates=None, stream_specification=None):
        update_kwargs = dict(TableName= table_name)
        if attribute_definitions:
            update_kwargs['AttributeDefinitions'       ] = attribute_definitions
        if gsi_updates:
            update_kwargs['GlobalSecondaryIndexUpdates'] = gsi_updates
        if stream_specification:
            update_kwargs['StreamSpecification'        ] = stream_specification

        return self.client().update_table(**update_kwargs )

    def tables(self):
        result = self.client().list_tables() or {}
        return result.get('TableNames') or []

    def streams(self):
        return self.client__dynamo_streams().list_streams().get('Streams')

    def random_id(self):
        import uuid
        return str(uuid.uuid4())