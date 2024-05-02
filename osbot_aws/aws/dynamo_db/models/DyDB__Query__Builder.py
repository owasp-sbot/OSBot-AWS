from decimal import Decimal
from typing import Union

from boto3.dynamodb.types import TypeSerializer

from osbot_aws.decorators.enforce_type_safety import enforce_type_safety
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.utils.Dev import pprint


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
    def set__attribute_name(self, name: str, value: str):
        return self.set__attribute_names({name : value})

    @enforce_type_safety
    def set__attribute_names(self, names_dict: dict):
        self.expression_attribute_names.update(names_dict)
        return self

    @enforce_type_safety
    def set__attribute_value(self, key: str, value: any):
        return self.set__attribute_values({key : value})

    @enforce_type_safety
    def set__attribute_values(self, values_dict: dict):
        for key, value in values_dict.items():
            self.expression_attribute_values[key] = self.serialize_value(value)
        return self

    @enforce_type_safety
    def set__update_expression(self, command  : str, target       : str, operation: str = None,
                               condition: str = None, default_value: str = None, new_value: str = None):
        if command == 'SET':
            if operation and condition:                                                         # Construct the conditional part if a condition and operation are specified
                conditional_part = f"{condition}({target}, {default_value})"
                expression =  f"SET {target} = {operation}({conditional_part}, {new_value})"
            elif operation:                                                                     # For operations without a condition (direct setting or transformations)
                expression = f"SET {target} = {operation}({new_value})"
            else:
                expression = f"SET {target} = {new_value}"                                      # Simple SET operation
        elif command == 'REMOVE':
            expression = f'REMOVE {target}'
        elif command == 'DELETE':
            expression = f'DELETE {target}'
        elif command == 'ADD':
            expression = f'ADD {target}'
        else:
            expression = ''
        self.update_expression = expression

    @enforce_type_safety
    def build__add_to_list(self, list_field_name: str, new_list_element: any):
        target = '#list_field_name'
        self.set__attribute_name (name=target, value=list_field_name)
        self.set__attribute_value(key =':new_element', value=[new_list_element])
        self.set__attribute_value(key =":empty_list", value=[])
        expression_kwargs = dict(operation     = 'list_append'    ,
                                 condition     = 'if_not_exists'  ,
                                 default_value = ':empty_list',
                                 new_value     = ':new_element'   )
        self.set__update_expression('SET', target, **expression_kwargs)
        return self.build()

    def build__add_to_set(self, field_name: str, element: any):
        target = '#field_name'
        self.set__attribute_name (name=target, value=field_name)
        self.set__attribute_value(key =':element', value={element})
        self.set__update_expression(command='ADD', target='#field_name :element')
        return self.build()

    def build__dict_add_to_set(self, dict_field:str, field_name: str, element: any):
        target = '#field_name'
        self.set__attribute_names({'#dict_field': dict_field,
                                   '#field_name': field_name})
        self.set__attribute_values({':element'  : {element} })
        self.set__update_expression(command='ADD', target='#dict_field.#field_name :element')
        return self.build()


    @enforce_type_safety
    def build__dict_delete_field(self, dict_field: str, field_key: str) -> dict:
        self.set__attribute_names({ '#dict_field': dict_field   ,
                                    '#key'       : field_key    })
        self.set__update_expression(command='REMOVE', target='#dict_field.#key')
        return self.build()

    @enforce_type_safety
    def build__delete_from_set(self, dict_field: str, field_name: str, element: any):
        self.set__attribute_names  (names_dict  = { '#dict_field': dict_field,
                                                    '#field_name' : field_name })
        self.set__attribute_values (values_dict = {':elements': {element}       })
        self.set__update_expression(command     = "DELETE"                              ,
                                    target      = f'#dict_field.#field_name :elements' )
        return self.build()
    @enforce_type_safety
    def build__dict_set_field(self, dict_field: str, field_key: str, field_value: any) -> dict:
        self.set__attribute_names ({'#dict_field': dict_field  ,
                                    '#key'       : field_key})
        self.set__attribute_values({':val'       : field_value})
        self.set__update_expression(command   = 'SET',
                                    target    = '#dict_field.#key',
                                    new_value = ':val')
        return self.build()

    @enforce_type_safety
    def build__dict_dict_set_field(self, parent_dict_field: str, child_dict_field: str, field_key: str, field_value: any) -> dict:
        self.set__attribute_names({'#parent_dict_field': parent_dict_field,
                                   '#child_dict_field' : child_dict_field,
                                   '#key'              : field_key})
        self.set__attribute_values({':val'             : field_value})
        self.set__update_expression(command='SET',
                                    target='#parent_dict_field.#child_dict_field.#key',
                                    new_value=':val')
        return self.build()

    @enforce_type_safety
    def build__dict_update_counter(self, dict_name, field_name: str, increment_by: Union[int, Decimal]):
        self.set__attribute_names({'#field_name': field_name,
                                   '#dict_name' : dict_name})
        self.set__attribute_values({':inc': increment_by})
        self.set__update_expression(command='ADD', target='#dict_name.#field_name :inc')
        return self.build()

    @enforce_type_safety
    def build__delete_field(self, field_name: str) -> dict:
        self.set__attribute_names  (names_dict = {'#field_name': field_name})
        self.set__update_expression(command    = 'REMOVE'                   ,
                                    target     = '#field_name'              )
        return self.build()

    @enforce_type_safety
    def build__delete_item_from_list(self, list_field_name : str, item_index : Union[int, Decimal]):
        self.set__attribute_names  (names_dict = {'#list_field_name': list_field_name  })
        self.set__update_expression(command    = "REMOVE"                               ,
                                    target     = f'#list_field_name[{item_index}]'      )
        return self.build()

    @enforce_type_safety
    def build__delete_elements_from_set(self, set_field_name: str, elements: set):
        self.set__attribute_names  (names_dict  = { '#set_field_name' : set_field_name })
        self.set__attribute_values (values_dict = {':elementsToRemove': elements       })
        self.set__update_expression(command     = "DELETE"                              ,
                                    target      = f'#set_field_name :elementsToRemove' )
        return self.build()

    @enforce_type_safety
    def build__set_field(self, field_name: str, field_value: any) -> dict:
        self.set__attribute_names  ({'#field_name' : field_name  })
        self.set__attribute_values ({':field_value': field_value })
        self.set__update_expression(command   = "SET"            ,
                                    target    = '#field_name'    ,
                                    new_value = ':field_value'   )
        return self.build()

    @enforce_type_safety
    def build__increment_field(self, field_name:str, increment_by:Union[int, Decimal]):
        self.set__attribute_names  ({ '#field_name': field_name })
        self.set__attribute_values ({ ':inc': increment_by      })
        self.set__update_expression(command='ADD',target='#field_name :inc')
        return self.build()

    def exp_key(self):
        return {self.key_name: self.serialize_value(self.key_value) }

    def serialize_value(self, value):
        return self.type_serializer().serialize(value)

    @cache_on_self
    def type_serializer(self):
        return TypeSerializer()