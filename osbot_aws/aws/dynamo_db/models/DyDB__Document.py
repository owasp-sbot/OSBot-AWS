from boto3.dynamodb.types import TypeSerializer, TypeDeserializer
from osbot_aws.aws.dynamo_db.domains.DyDB__Table        import DyDB__Table
from osbot_aws.aws.dynamo_db.models.DyDB__Query__Builder import DyDB__Query__Builder
from osbot_utils.base_classes.Kwargs_To_Self            import Kwargs_To_Self
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from osbot_utils.decorators.methods.remove_return_value import remove_return_value
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Json                             import to_json_str
from osbot_utils.utils.Misc                             import list_set



class DyDB__Document(Kwargs_To_Self):
    table           : DyDB__Table
    document        : dict

    def __repr__(self):
        return f'[DyDB__Document]\n' + to_json_str(self.document)

    # support methods
    def db_query_builder(self):
        kwargs = dict(table_name = self.table.table_name,
                      key_name   = self.table.key_name,
                      key_value   = self.document_id())
        return DyDB__Query__Builder(**kwargs)

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

    def add_field(self, field_name, field_value):
        return self.set_field(field_name=field_name, field_value=field_value)

    def add_to_list(self, list_field_name, new_list_element):
        #exp_update  = f"SET {list_field_name} = list_append(if_not_exists({list_field_name}, :empty_list), :new_element)"
        # kwargs      = dict(TableName                 = self.table.table_name                                             ,
        #                    Key                       = self.exp_key()                                                    ,
        #                    UpdateExpression          = exp_update                                                        ,
        #                    ExpressionAttributeValues = { ':new_element': self.serialize_value([new_list_element]) ,       # new element must be wrapped in a list
        #                                                  ':empty_list' : self.serialize_value([])                },       # default empty list if the list does not exist
        #                    ReturnValues              = 'UPDATED_NEW'                                                           )       # Returns the updated list

        kwargs   = self.db_query_builder().build__add_to_list(list_field_name, new_list_element)
        response = self.client().update_item(**kwargs)
        return response.get('Attributes')

    def dict_delete_field(self, dict_field, field_key):
        # kwargs = {'TableName'                   : self.table.table_name,
        #           'Key'                         : self.exp_key()                ,
        #           'UpdateExpression'            : f'REMOVE #dict_field.#key'    ,
        #           'ExpressionAttributeNames'    : { '#dict_field': dict_field   ,
        #                                             '#key'       : field_key    },
        #           'ReturnValues'                : 'NONE'}
        kwargs = self.db_query_builder().build__dict_delete_field(dict_field, field_key)
        self.client().update_item(**kwargs)
        return self

    def dict_set_field(self, dict_field, field_key, field_value):
        kwargs = self.db_query_builder().build__dict_set_field(dict_field, field_key, field_value)
        # kwargs = {'TableName'                   : self.table.table_name,
        #           'Key'                         : self.exp_key()                ,
        #           'UpdateExpression'            : f'SET #dict_field.#key = :val',
        #           'ExpressionAttributeNames'    : { '#dict_field': dict_field ,
        #                                             '#key'       : field_key        },
        #           'ExpressionAttributeValues'   : { ':val': self.serialize_value(field_value)  },
        #           'ReturnValues'                : 'NONE'}
        self.client().update_item(**kwargs)
        return self

    def delete_field(self, field_name):
        if field_name not in self.fields():
            return False
        kwargs = self.db_query_builder().build__delete_field(field_name)
        self.client().update_item(**kwargs)
        return True

    def delete_item_from_list(self, list_field_name, item_index):
        kwargs = self.db_query_builder().build__delete_item_from_list(list_field_name, item_index)
        # exp_update = f"REMOVE #list_field_name[{item_index}]"
        # kwargs = dict(TableName                = self.table.table_name,
        #               Key                      = self.exp_key(),
        #               UpdateExpression         = exp_update,
        #               ExpressionAttributeNames = { '#list_field_name': list_field_name  },
        #               ReturnValues='NONE' )

        self.client().update_item(**kwargs)
        return self

    def delete_element_from_set(self, set_field_name, element):
        return self.delete_elements_from_set(set_field_name=set_field_name, elements={element})

    def delete_elements_from_set(self, set_field_name, elements):
        if type(elements) is not set:
            raise ValueError(f"in delete_elements_from_set, the type of elements must be set and it was {type(elements)}")

        kwargs = self.db_query_builder().build__delete_elements_from_set(set_field_name, elements)
        exp_update = f"DELETE #set_field_name :elementsToRemove"
        # elements_to_remove = self.serialize_value(elements)
        # kwargs = dict(TableName                 = self.table.table_name,
        #               Key                       = self.exp_key(),
        #               UpdateExpression          = exp_update,
        #               ExpressionAttributeNames  = { '#set_field_name': set_field_name   },
        #               ExpressionAttributeValues = { ':elementsToRemove': elements_to_remove },
        #               ReturnValues              = 'NONE' )

        self.client().update_item(**kwargs)

        return self

    def reset_document(self):
        new_document  = {'id': self.document_id()}
        self.document =  self.table.add_document(new_document).get('document')
        return self

    def set_document(self,new_document):
        new_document[self.key_name()] = self.key_value()                             # make sure the id value is the same
        self.document = self.table.add_document(new_document).get('document')
        return self

    @remove_return_value(field_name='ResponseMetadata')
    def set_field(self, field_name, field_value):
        kwargs = self.db_query_builder().build__set_field(field_name, field_value)
        # kwargs = dict(TableName                 = self.table.table_name,
        #               Key                       = self.exp_key(),
        #               UpdateExpression          = 'SET #field_name = :field_value',
        #               ExpressionAttributeNames  = {'#field_name': field_name},
        #               ExpressionAttributeValues = {':field_value': self.serialize_value(field_value)},
        #               ReturnValues              = 'NONE')

        self.client().update_item(**kwargs)
        return self

    def update_counter(self, field_name, increment_by):
        kwargs = self.db_query_builder().build__update_counter(field_name, increment_by)
        # kwargs = dict(TableName                 = self.table.table_name              ,
        #               Key                       = self.exp_key()                     ,
        #               UpdateExpression          = f'ADD #field_name :inc'            ,
        #               ExpressionAttributeNames  = { '#field_name': field_name}       ,
        #               ExpressionAttributeValues = { ':inc': {'N': str(increment_by)}},
        #               ReturnValues              = 'UPDATED_NEW'                      )

        self.client().update_item(**kwargs)
        return self