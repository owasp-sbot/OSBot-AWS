import pytest

from osbot_aws.aws.dynamo_db.domains.DyDB__Table__Resources import DyDB__Table__Resources, KEY_NAME__TABLE__RESOURCES, \
    Resource__Config
from osbot_aws.aws.dynamo_db.models.DyDB__Document import DyDB__Document
from osbot_aws.aws.dynamo_db.models.DyDB__Resource import DyDB__Resource
from osbot_aws.testing.TestCase__Dynamo_DB import TestCase__Dynamo_DB
from osbot_aws.testing.TestCase__Dynamo_DB__Local import TestCase__Dynamo_DB__Local
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.testing.Duration import Duration
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set
from osbot_utils.utils.Objects import obj_info, base_types



class test_DyDB__Table__Resources(TestCase__Dynamo_DB__Local):
    temp_dydb_table_resources: DyDB__Table__Resources
    table_name               : str                    = 'temp_dydb_table_resources'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.temp_dydb_table_resources = DyDB__Table__Resources(table_name=cls.table_name, dynamo_db=cls.dynamo_db)
        assert cls.temp_dydb_table_resources.create_table() is True

    @classmethod
    def tearDownClass(cls):
        assert cls.temp_dydb_table_resources.delete_table() is True
        super().tearDownClass()
        assert cls.temp_dydb_table_resources.exists()       is False


    def test__setUpClass(self):
        with self.temp_dydb_table_resources as _:
            assert _.exists() is True
            assert _.key_name == KEY_NAME__TABLE__RESOURCES

    def test_resources(self):
        with self.temp_dydb_table_resources as _:
            assert list_set(_.resources())     == ['config']
            config = _.resource('config')
            assert type(config)       is Resource__Config
            assert base_types(config) == [DyDB__Resource, DyDB__Document, Kwargs_To_Self, object]

    
    def test_resource(self):
        config_resource = self.temp_dydb_table_resources.resource('config')
        with config_resource as _:
            _.reload()
            new_value = 'new_version'
            _.version__update(new_value)
            assert _.version()                == new_value
            assert _.field('version')         == new_value
            assert _.document.get('version')  == new_value


    def test_resource__raw_commands(self):
        config_resource = self.temp_dydb_table_resources.resource('config')
        with config_resource as _:
            _.set_field (field_name='an_set', field_value={'now', 'as a set'})
            _.add_to_set(field_name= 'an_set',element    = 'extra one'       )
            _.reload()

            value_after_add    = _.value('an_set')
            _.delete_from_set('an_set', 'as a set')
            _.reload()

            value_after_delete = _.value('an_set')

            assert value_after_add    == {'now', 'as a set', 'extra one'}
            assert value_after_delete == {'now', 'extra one'}

            _.set_field           ('an_dict',  { 'an_inner_set': {'element_1', 'element_2'}})
            _.dict_add_to_set     ('an_dict', 'an_inner_set', 'element_3')
            _.dict_delete_from_set('an_dict', 'an_inner_set', 'element_2')
            _.reload()
            assert _.value('an_dict').get('an_inner_set') == {'element_1', 'element_3'}



