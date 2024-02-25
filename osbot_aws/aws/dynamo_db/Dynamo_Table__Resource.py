from boto3 import resource

from osbot_aws.aws.dynamo_db.Dynamo_DB import Dynamo_DB
from osbot_utils.utils.Lists import array_pop
from osbot_utils.utils.Objects import get_value

# todo: see if we can remove this class once the new Dynamo_DB__Table is implemented
class Dynamo_Table__Resource:
    def __init__(self,table_name, key):
        self.table_name = table_name
        self.key        = key
        self.dynamo     = Dynamo_DB()
        self.resource   = resource('dynamodb')          # this has quite a lot of weird performance implications
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
            return self.dynamo.client().describe_table(TableName = self.table_name)
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
        streams   = self.dynamo.client__dynamo_streams().list_streams(TableName=self.table_name).get('Streams')
        first_one = array_pop(streams,0)
        return get_value(first_one,'StreamArn')

    def stream_info(self):
        stream_arn = self.stream_arn()
        if stream_arn:
            return self.dynamo.client__dynamo_streams().describe_stream(StreamArn=stream_arn).get('StreamDescription')

    def stream_get_data_latest(self):
        stream_info    = self.stream_info()
        shard_id       = stream_info.get('Shards').pop(0).get('ShardId')
        shard_iterator = self.dynamo.client__dynamo_streams().get_shard_iterator(StreamArn=self.stream_arn(), ShardId=shard_id, ShardIteratorType='LATEST').get('ShardIterator')
        return           self.dynamo.client__dynamo_streams().get_records(ShardIterator=shard_iterator)

        #shard_iterator = get_shard_iterator

    def status(self):
        return self.info()['Table']['TableStatus']