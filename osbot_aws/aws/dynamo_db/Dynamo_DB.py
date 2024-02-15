from functools import cache

from   boto3    import resource
from osbot_aws.apis.Session import Session


class Dynamo_DB:
    def __init__(self):
        pass
        #self.resource   = resource('dynamodb')
        self._dynamo    = None
        self._streams   = None

    # helpers
    @cache
    def dynamo(self):
        return Session().client('dynamodb')

    @cache
    def dynamo_streams(self):
        return Session().client('dynamodbstreams')
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
