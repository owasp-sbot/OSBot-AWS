import boto3
from   boto3    import resource

from osbot_aws.apis.Session import Session


class Dynamo:
    def __init__(self):
        self.resource   = resource('dynamodb')
        self.client     = Session().client('dynamodb')

    def create(self, table_name, key):
        keySchema             = [ {'AttributeName'    : key        , 'KeyType'           : 'HASH' } ]
        attributeDefinitions  = [ {'AttributeName'    : key        , 'AttributeType'     : 'S'    } ]
        provisionedThroughput = { 'ReadCapacityUnits' : 5          , 'WriteCapacityUnits': 5      }
        self.client.create_table( TableName             = table_name           ,
                                  KeySchema             = keySchema            ,
                                  AttributeDefinitions  = attributeDefinitions ,
                                  ProvisionedThroughput = provisionedThroughput)
        self.client.get_waiter('table_exists') \
            .wait(TableName=table_name, WaiterConfig={'Delay': 2, 'MaxAttempts': 10})

    def delete(self, table_name):
        self.client.delete_table(TableName = table_name)
        self.client.get_waiter('table_not_exists')      \
                   .wait(TableName=table_name, WaiterConfig={'Delay': 2, 'MaxAttempts':10 })

    def list(self):
        return self.client.list_tables()['TableNames']

class Dynamo_Table:
    def __init__(self,table_name, key):
        self.table_name = table_name
        self.key        = key
        self.dynamo     = Dynamo()
        self.client     = self.dynamo.client
        self.resource   = self.dynamo.resource
        self.table      = self.resource.Table(self.table_name)
        self.chuck_size = 100

        self._keys      = None

    def add(self,row):
        self.table.put_item(Item=row)
        return row

    def add_batch(self, items):
        with self.table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)

    def delete(self, item):
        self.table.delete_item(Key= { self.key : item })

    def delete_batch(self, items):
        with self.table.batch_writer() as batch:
            for item in items:
                batch.delete_item(Key= item )

    def exists(self):
        if self.info():
            return True
        return False

    def get(self, key_value):
        data = self.table.get_item(Key={self.key: key_value})
        return data.get('Item')

    def get_batch(self, keys):
        def chunks(items,split):
            for i in range(0, len(items), split):
                yield items[i:i + split]

        for chunck in chunks(keys, self.chuck_size):
            request_items = []
            for key in chunck:
                request_items.append({self.key:  key })
            response = self.resource.batch_get_item(RequestItems={self.table_name: {'Keys': request_items}})
            yield response['Responses'][self.table_name]

    def info(self):
        try:
            return self.client.describe_table(TableName = self.table_name)
        except:
            return None

    def keys(self):
        if self._keys:
            return self._keys
        def get_scan_batch (start_key):
            if start_key:
                return self.table.scan(ProjectionExpression=self.key, ExclusiveStartKey =start_key );
            else:
                return self.table.scan(ProjectionExpression=self.key)

        keys = []

        def map_Items(items):
            for item in items:
                 keys.append(item[self.key])
            #print(len(items))

        response = get_scan_batch(None)                                 # first call
        map_Items(response['Items'])                                    # map items
        while 'LastEvaluatedKey' in response:                           # see if we need to page
            response = get_scan_batch(response.get('LastEvaluatedKey')) # call with LastEvaluatedKey
            map_Items(response['Items'])                                # map items

        self._keys = keys

        return keys

    def status(self):

        return self.info()['Table']['TableStatus']