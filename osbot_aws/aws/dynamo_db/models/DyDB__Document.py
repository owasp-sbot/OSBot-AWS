from boto3.dynamodb.types import TypeSerializer, TypeDeserializer
from osbot_aws.aws.dynamo_db.domains.DyDB__Table        import DyDB__Table
from osbot_utils.base_classes.Kwargs_To_Self            import Kwargs_To_Self
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from osbot_utils.decorators.methods.remove_return_value import remove_return_value
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Json                             import to_json_str
from osbot_utils.utils.Misc                             import list_set


class DyDB__Document(Kwargs_To_Self):
    table     : DyDB__Table
    document  : dict

    def __repr__(self):
        return f'[DyDB__Document]\n' + to_json_str(self.document)

    # support methods

    def client(self):
        return self.table.dynamo_db.client()

    def document_id(self):
        return self.key_value()

    def fields(self):
        return list_set(self.document)

    def exp_key(self):
        return {self.key_name(): self.serialize_value(self.key_value()) }

    def key_name(self):
        return self.table.key_name

    def key_value(self):
        return self.document.get(self.key_name())

    def reload(self):
        self.document = self.table.document(self.document_id())
        return self.document

    def serialize_value(self, value):
        return self.type_serializer().serialize(value)

    def deserialize_value(self, value):
        return self.type_deserializer().deserialize(value)

    @cache_on_self
    def type_deserializer(self):
        return TypeDeserializer()

    @cache_on_self
    def type_serializer(self):
        return TypeSerializer()

    # action methods

    def add_to_list(self, list_field_name, new_list_element):
        exp_update  = f"SET {list_field_name} = list_append(if_not_exists({list_field_name}, :empty_list), :new_element)"
        kwargs      = dict(TableName                 = self.table.table_name                                             ,
                           Key                       = self.exp_key()                                                    ,
                           UpdateExpression          = exp_update                                                        ,
                           ExpressionAttributeValues = { ':new_element': self.serialize_value([new_list_element]) ,       # new element must be wrapped in a list
                                                         ':empty_list' : self.serialize_value([])                },       # default empty list if the list does not exist
                           ReturnValues              = 'UPDATED_NEW'                                                           )       # Returns the updated list
        response = self.client().update_item(**kwargs)
        return response.get('Attributes')

    def delete_field(self, field_name):
        if field_name not in self.fields():
            return False
        kwargs = dict( TableName                 = self.table.table_name      ,
                        Key                      = self.exp_key()             ,
                        UpdateExpression         = f'REMOVE #field_name'      ,
                        ExpressionAttributeNames = {'#field_name': field_name},
                        ReturnValues             = 'ALL_NEW'                  ) # todo make it configurable and default should be NONE

        result        = self.client().update_item(**kwargs)                     # todo refactor this logic in a method that is used by all update methods
        raw_document  = result.get('Attributes')
        self.document = self.table.dynamo_db.document_deserialize(raw_document)
        return True

    def delete_item_from_list(self, list_field_name, item_index):
        exp_update = f"REMOVE #list_field_name[{item_index}]"
        kwargs = dict(TableName=self.table.table_name,
                      Key=self.exp_key(),
                      UpdateExpression=exp_update,
                      ExpressionAttributeNames={ '#list_field_name': list_field_name  },
                      ReturnValues='NONE' )

        self.client().update_item(**kwargs)

    def reset_document(self):
        new_document  = {'id': self.document_id()}
        self.document =  self.table.add_document(new_document).get('document')
        return self

    def set_dict_field(self, dict_field, field_key, field_value):

        kwargs = {'TableName'                   : self.table.table_name,
                  'Key'                         : self.exp_key()                ,
                  'UpdateExpression'            : f'SET #dict_field.#key = :val',
                  'ExpressionAttributeNames'    : { '#dict_field': dict_field ,
                                                    '#key'       : field_key        },
                  'ExpressionAttributeValues'   : { ':val': self.serialize_value(field_value)  },
                  'ReturnValues'                : 'NONE'}
        self.client().update_item(**kwargs)
        return self

    def set_document(self,new_document):
        new_document[self.key_name()] = self.key_value()                             # make sure the id value is the same
        self.document = self.table.add_document(new_document).get('document')
        return self

    @remove_return_value(field_name='ResponseMetadata')
    def set_field(self, field_name, field_value):
        kwargs = dict(TableName=self.table.table_name,
                      Key=self.exp_key(),
                      UpdateExpression='SET #field_name = :field_value',
                      ExpressionAttributeNames={'#field_name': field_name},
                      ExpressionAttributeValues={':field_value': self.serialize_value(field_value)},
                      ReturnValues='NONE')

        self.client().update_item(**kwargs)
        return self