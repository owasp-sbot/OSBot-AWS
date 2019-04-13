import boto3
from   boto3    import resource
from pbx_gs_python_utils.utils.Misc import Misc

from osbot_aws.apis.Session import Session


class Dynamo:
    def __init__(self):
        self.resource   = resource('dynamodb')
        self._dynamo    = None
        self._streams   = None

    # helpers

    def dynamo(self):
        if self._dynamo is None:
            self._dynamo = Session().client('dynamodb')
        return self._dynamo

    def dynamo_streams(self):
        if self._streams is None:
            self._streams = Session().client('dynamodbstreams')
        return self._streams
    # main methods

    def create(self, table_name, key, with_streams=False):
        keySchema             = [ {'AttributeName'    : key        , 'KeyType'           : 'HASH' } ]
        attributeDefinitions  = [ {'AttributeName'    : key        , 'AttributeType'     : 'S'    } ]
        provisionedThroughput = { 'ReadCapacityUnits' : 5          , 'WriteCapacityUnits': 5      }
        kwargs   = { 'TableName'            : table_name           ,
                     'KeySchema'            : keySchema            ,
                     'AttributeDefinitions' : attributeDefinitions ,
                     'ProvisionedThroughput': provisionedThroughput }
        if with_streams:
            kwargs['StreamSpecification'] = {'StreamEnabled': True, 'StreamViewType': 'NEW_IMAGE' }
        self.dynamo().create_table( **kwargs)

        self.dynamo().get_waiter('table_exists') \
            .wait(TableName=table_name, WaiterConfig={'Delay': 5, 'MaxAttempts': 10})
        return self

    def delete(self, table_name):
        self.dynamo().delete_table(TableName = table_name)
        self.dynamo().get_waiter('table_not_exists')      \
                   .wait(TableName=table_name, WaiterConfig={'Delay': 10, 'MaxAttempts':10 })
        return self

    def list(self):
        return self.dynamo().list_tables()['TableNames']

    def streams(self):
        return self.dynamo_streams().list_streams().get('Streams')

class Dynamo_Table:
    def __init__(self,table_name, key):
        self.table_name = table_name
        self.key        = key
        self.dynamo     = Dynamo()
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
            return self.dynamo.dynamo().describe_table(TableName = self.table_name)
        except:
            return None

    def keys(self, use_cache=True):
        if self._keys and use_cache:
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

    def stream_arn(self):
        streams   = self.dynamo.dynamo_streams().list_streams(TableName=self.table_name).get('Streams')
        first_one = Misc.array_pop(streams,0)
        return Misc.get_value(first_one,'StreamArn')

    def stream_info(self):
        stream_arn = self.stream_arn()
        if stream_arn:
            return self.dynamo.dynamo_streams().describe_stream(StreamArn=stream_arn).get('StreamDescription')

    def stream_get_data_latest(self):
        stream_info    = self.stream_info()
        shard_id       = stream_info.get('Shards').pop(0).get('ShardId')
        shard_iterator = self.dynamo.dynamo_streams().get_shard_iterator(StreamArn=self.stream_arn(), ShardId=shard_id, ShardIteratorType='LATEST').get('ShardIterator')
        return           self.dynamo.dynamo_streams().get_records(ShardIterator=shard_iterator)

        #shard_iterator = get_shard_iterator

    def status(self):
        return self.info()['Table']['TableStatus']