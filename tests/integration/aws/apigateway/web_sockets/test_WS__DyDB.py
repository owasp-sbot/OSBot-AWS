import pytest

from osbot_aws.aws.apigateway.apigw_dydb.WS__DyDB import WS__DyDB, DYNAMO_DB__TABLE_NAME__WEB_SOCKETS, \
    TABLE_WEB_SOCKETS__INDEXES_NAMES
from osbot_aws.testing.TestCase__Dynamo_DB import TestCase__Dynamo_DB
from osbot_aws.utils.Execution_Env import current_execution_env


class test_WS__DyDB(TestCase__Dynamo_DB):
    dydb_ws: WS__DyDB
    source : str
    env    : str

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env     = current_execution_env()
        cls.dydb_ws = WS__DyDB(dynamo_db=cls.dynamo_db)

    def test__create_table(self):
        with self.dydb_ws as _:
            if _.exists() is False:
                assert self.dydb_ws.dynamo_db.client().meta.region_name == 'eu-west-1'              # todo: move to OSBot test config
                assert _.table_name == DYNAMO_DB__TABLE_NAME__WEB_SOCKETS
                # dydb_ws.delete_table(wait_for_deletion=True)
                assert _.create_table(wait_for_table=False)  is True

    def test__init__(self):
        table_name = DYNAMO_DB__TABLE_NAME__WEB_SOCKETS.format(env=self.env)
        expected_vars = {'dynamo_db'    : self.dynamo_db                    ,
                         'env'          : self.dydb_ws.env                  ,
                         'key_name'     : 'id'                              ,
                         'key_type'     : 'S'                               ,
                         'table_indexes': TABLE_WEB_SOCKETS__INDEXES_NAMES ,
                         'table_name'   : table_name                        }
        assert self.dydb_ws.__locals__() == expected_vars
        assert self.dydb_ws.exists() is True
