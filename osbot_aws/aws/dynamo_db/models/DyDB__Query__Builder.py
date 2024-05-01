from decimal import Decimal
from typing import Union

from boto3.dynamodb.types import TypeSerializer

from osbot_aws.decorators.enforce_type_safety import enforce_type_safety
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

    @enforce_type_safety
    def build__add_to_list(self, list_field_name: str, new_list_element: any):
        self.expression_attribute_values = {':new_element': self.serialize_value([new_list_element]),
                                            ':empty_list': self.serialize_value([])}
        self.update_expression = f"SET {list_field_name} = list_append(if_not_exists({list_field_name}, :empty_list), :new_element)"
        return self.build()

    @enforce_type_safety
    def build__dict_delete_field(self, dict_field: str, field_key: str) -> dict:
        self.expression_attribute_names = { '#dict_field': dict_field   ,
                                            '#key'       : field_key    }
        self.update_expression = f'REMOVE #dict_field.#key'
        return self.build()

    @enforce_type_safety
    def build__dict_set_field(self, dict_field: str, field_key: str, field_value: any) -> dict:
        self.expression_attribute_names = { '#dict_field': dict_field ,
                                             '#key'       : field_key }
        self.expression_attribute_values = { ':val': self.serialize_value(field_value)  }
        self.update_expression = f'SET #dict_field.#key = :val'
        return self.build()

    @enforce_type_safety
    def build__delete_field(self, field_name: str) -> dict:
        self.expression_attribute_names = {'#field_name': field_name}
        self.update_expression          = f'REMOVE #field_name'
        return self.build()

    @enforce_type_safety
    def build__delete_item_from_list(self, list_field_name : str, item_index : Union[int, Decimal]):
        exp_update                      = f"REMOVE #list_field_name[{item_index}]"
        self.expression_attribute_names = { '#list_field_name': list_field_name  }
        self.update_expression = exp_update
        return self.build()

    @enforce_type_safety
    def build__delete_elements_from_set(self, set_field_name: str, elements: set):
        exp_update = f"DELETE #set_field_name :elementsToRemove"
        elements_to_remove = self.serialize_value(elements)
        self.expression_attribute_names  = { '#set_field_name' : set_field_name     }
        self.expression_attribute_values = {':elementsToRemove': elements_to_remove }
        self.update_expression = exp_update
        return self.build()

    @enforce_type_safety
    def build__set_field(self, field_name: str, field_value: any) -> dict:
        self.expression_attribute_names =  {'#field_name' : field_name                       }
        self.expression_attribute_values = {':field_value': self.serialize_value(field_value)}
        self.update_expression ='SET #field_name = :field_value'
        return self.build()

    @enforce_type_safety
    def build__update_counter(self, field_name:str, increment_by:Union[int, Decimal]):
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