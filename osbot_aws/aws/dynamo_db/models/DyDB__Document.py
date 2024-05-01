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
        kwargs   = self.db_query_builder().build__add_to_list(list_field_name, new_list_element)
        response = self.client().update_item(**kwargs)
        return response.get('Attributes')

    def dict_delete_field(self, dict_field, field_key):
        kwargs = self.db_query_builder().build__dict_delete_field(dict_field, field_key)
        self.client().update_item(**kwargs)
        return self

    def dict_set_field(self, dict_field, field_key, field_value):
        kwargs = self.db_query_builder().build__dict_set_field(dict_field, field_key, field_value)
        self.client().update_item(**kwargs)
        return self

    def dict_update_counter(self, dict_field, field_name, increment_by):
        kwargs = self.db_query_builder().build__dict_update_counter(dict_field, field_name, increment_by)
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
        self.client().update_item(**kwargs)
        return self

    def delete_element_from_set(self, set_field_name, element):
        return self.delete_elements_from_set(set_field_name=set_field_name, elements={element})

    def delete_elements_from_set(self, set_field_name, elements):
        kwargs = self.db_query_builder().build__delete_elements_from_set(set_field_name, elements)
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
        self.client().update_item(**kwargs)
        return self

    def update_counter(self, field_name, increment_by):
        kwargs = self.db_query_builder().build__update_counter(field_name, increment_by)
        self.client().update_item(**kwargs)
        return self

