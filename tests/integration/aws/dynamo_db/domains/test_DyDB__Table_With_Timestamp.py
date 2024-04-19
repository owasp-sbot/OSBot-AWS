from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.aws.dynamo_db.Dynamo_DB__Table import Dynamo_DB__Table
from osbot_aws.aws.dynamo_db.domains.DyDB__Table import DyDB__Table
from osbot_aws.aws.dynamo_db.domains.DyDB__Table_With_GSI import DyDB__Table_With_GSI
from osbot_aws.aws.dynamo_db.domains.DyDB__Table_With_Timestamp import DyDB__Table_With_Timestamp
from osbot_aws.testing.TestCase__Dynamo_DB import TestCase__Dynamo_DB
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Objects import base_types


class test_DyDB__Table_With_Timestamp(TestCase__Dynamo_DB):
    delete_on_exit            : bool = False  # in_github_action() # can't really do this since it takes ages (like several minutes for the GSIs to be created)
    aws_config                : AWS_Config
    dydb_table_with_timestamp : DyDB__Table_With_Timestamp
    table_name                : str = f'pytest__dydb__table_with_timestamp'
    account_id                : str
    region_name               : str

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dydb_table_with_timestamp = DyDB__Table_With_Timestamp(table_name=cls.table_name,
                                                                   dynamo_db=cls.dynamo_db)  # set dynamo_db to version of dynamo_db from TestCase__Dynamo_DB (which has the correct IAM permissions)
        cls.aws_config  = AWS_Config()
        cls.region_name = cls.aws_config.region_name()
        cls.account_id  = cls.aws_config.account_id()
        #cls.dydb_table_with_timestamp.create_table()           # create if it doesn't exist
        with cls.dydb_table_with_timestamp as _:
            _.table_indexes = ['user_id', 'role', 'path']       # default table indexes

    @classmethod
    def tearDownClass(cls):
        if cls.delete_on_exit:
            assert cls.dydb_table_with_timestamp.delete_table(wait_for_deletion=False) is True

    def test__init__(self):
        assert self.region_name == 'eu-west-1'
        expected_var = {'dynamo_db'    : self.dynamo_db ,
                        'key_name'     : 'id'           ,
                        'key_type'     : 'S'            ,
                        'table_indexes': ['user_id', 'role', 'path']  ,
                        'table_name'   : self.table_name}
        with self.dydb_table_with_timestamp as _:
            assert _.__locals__() == expected_var
            assert base_types(_)  == [ DyDB__Table_With_GSI ,
                                       DyDB__Table          ,
                                       Dynamo_DB__Table     ,
                                       Kwargs_To_Self       ,
                                       object               ]

    def test_AAA_setup(self):
        with self.dydb_table_with_timestamp as _:
            _.setup()
            assert _.exists() is True

    def test_indexes_exist(self):
        with self.dydb_table_with_timestamp as _:
            assert _.indexes_exist() is False