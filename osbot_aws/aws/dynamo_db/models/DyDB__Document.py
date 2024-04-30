from boto3.dynamodb.types                               import TypeSerializer
from osbot_aws.aws.dynamo_db.domains.DyDB__Table        import DyDB__Table
from osbot_utils.base_classes.Kwargs_To_Self            import Kwargs_To_Self
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from osbot_utils.decorators.methods.remove_return_value import remove_return_value
from osbot_utils.utils.Json                             import to_json_str
from osbot_utils.utils.Misc                             import list_set


class DyDB__Document(Kwargs_To_Self):
    table     : DyDB__Table
    document  : dict

    def __repr__(self):
        return f'[DyDB__Document]\n' + to_json_str(self.document)

    @remove_return_value(field_name='ResponseMetadata')
    def add_field(self, field_name, field_value):

        kwargs = dict(TableName                 = self.table.table_name                         ,
                      Key                       = self.exp_key()                                ,
                      UpdateExpression          = 'SET #field_name = :field_value'              ,
                      ExpressionAttributeNames  = { '#field_name': field_name                   },
                      ExpressionAttributeValues = { ':field_value': self.serialize(field_value) },
                      ReturnValues              = 'UPDATED_NEW'                                 )

        response = self.client().update_item(**kwargs)
        return response

    def client(self):
        return self.table.dynamo_db.client()

    def document_id(self):
        return self.key_value()

    def fields(self):
        return list_set(self.document)

    def exp_key(self):
        return {self.key_name(): self.serialize(self.key_value()) }

    def key_name(self):
        return self.table.key_name

    def key_value(self):
        return self.document.get(self.key_name())

    def reload(self):
        self.document = self.table.document(self.document_id())
        return self.document

    def serialize(self, value):
        return self.type_serializer().serialize(value)

    @cache_on_self
    def type_serializer(self):
        return TypeSerializer()

