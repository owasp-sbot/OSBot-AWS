from boto3.dynamodb.types import TypeSerializer

from osbot_aws.aws.dynamo_db.domains.DyDB__Table import DyDB__Table
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.decorators.methods.remove_return_value import remove_return_value
from osbot_utils.utils.Dev import pprint


class DyDB__Table_Update(DyDB__Table):

    @remove_return_value(field_name='ResponseMetadata')
    def update_add_field(self, key_value, field_name, field_value, field_type='S'):

        kwargs = dict(TableName                 = self.table_name                               ,
                      Key                       = { self.key_name: self.serialize(key_value)    },
                      UpdateExpression          = 'SET #field_name = :field_value'              ,
                      ExpressionAttributeNames  = { '#field_name': field_name                   },
                      ExpressionAttributeValues = { ':field_value': self.serialize(field_value) },
                      ReturnValues              = 'UPDATED_NEW'                                 )

        response = self.dynamo_db.client().update_item(**kwargs)
        return response

    @cache_on_self
    def type_serializer(self):
        return TypeSerializer()

    def serialize(self, value):
        return self.type_serializer().serialize(value)

