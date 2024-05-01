from decimal import Decimal

from boto3.dynamodb.types import TypeSerializer

from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.decorators.methods.cache_on_self import cache_on_self


class DyDB__Query__Builder(Kwargs_To_Self):
    table_name                  : str
    key_name                    : str
    key_value                   : str
    expression_attribute_names  : dict
    expression_attribute_values : dict
    update_expression           : str
    return_values               : str = 'NONE'
    kwargs                      : dict

    def build(self):
        self.kwargs['Key'                       ] = self.exp_key()
        self.kwargs['ReturnValues'              ] = self.return_values
        self.kwargs['TableName'                 ] = self.table_name
        self.kwargs['UpdateExpression'          ] = self.update_expression
        if self.expression_attribute_values:
            self.kwargs['ExpressionAttributeValues' ] = self.expression_attribute_values
        if self.expression_attribute_names:
            self.kwargs['ExpressionAttributeNames'  ] = self.expression_attribute_names

        return self.kwargs

    def build__add_to_list(self, list_field_name, new_list_element):
        self.expression_attribute_values = {':new_element': self.serialize_value([new_list_element]),
                                            ':empty_list': self.serialize_value([])}
        self.update_expression = f"SET {list_field_name} = list_append(if_not_exists({list_field_name}, :empty_list), :new_element)"
        return self.build()

    def build__dict_delete_field(self, dict_field, field_key):
        self.expression_attribute_names = { '#dict_field': dict_field   ,
                                            '#key'       : field_key    }
        self.update_expression = f'REMOVE #dict_field.#key'
        return self.build()

    def build__dict_set_field(self, dict_field, field_key, field_value):
        self.expression_attribute_names = { '#dict_field': dict_field ,
                                             '#key'       : field_key }
        self.expression_attribute_values = { ':val': self.serialize_value(field_value)  }
        self.update_expression = f'SET #dict_field.#key = :val'
        return self.build()

    def build__delete_field(self, field_name):
        self.expression_attribute_names = {'#field_name': field_name}
        self.update_expression          = f'REMOVE #field_name'
        return self.build()

    def build__delete_item_from_list(self, list_field_name, item_index):
        if not isinstance(item_index, int):
            raise ValueError(f"in build__delete_item_from_list Item index must be an integer, but it was an {type(item_index)}")

        exp_update                      = f"REMOVE #list_field_name[{item_index}]"
        self.expression_attribute_names = { '#list_field_name': list_field_name  }
        self.update_expression = exp_update
        return self.build()


    def build__delete_elements_from_set(self, set_field_name, elements):
        if type(elements) is not set:
            raise ValueError(f"in delete_elements_from_set, the type of elements must be set and it was {type(elements)}")

        exp_update = f"DELETE #set_field_name :elementsToRemove"
        elements_to_remove = self.serialize_value(elements)
        self.expression_attribute_names  = { '#set_field_name' : set_field_name     }
        self.expression_attribute_values = {':elementsToRemove': elements_to_remove }
        self.update_expression = exp_update
        return self.build()

    def build__set_field(self, field_name, field_value):
        self.expression_attribute_names =  {'#field_name' : field_name                       }
        self.expression_attribute_values = {':field_value': self.serialize_value(field_value)}
        self.update_expression ='SET #field_name = :field_value'
        return self.build()

    def build__update_counter(self, field_name, increment_by):
        if not isinstance(increment_by, int) and not isinstance(increment_by, Decimal):
            raise ValueError(f"in build__update_counter increment value must be an integer and it was an {type(increment_by)}")

        self.expression_attribute_names  = { '#field_name': field_name       }
        self.expression_attribute_values = { ':inc': {'N': str(increment_by)}}
        self.update_expression =f'ADD #field_name :inc'
        return self.build()

    def exp_key(self):
        return {self.key_name: self.serialize_value(self.key_value) }

    def serialize_value(self, value):
        return self.type_serializer().serialize(value)

    @cache_on_self
    def type_serializer(self):
        return TypeSerializer()