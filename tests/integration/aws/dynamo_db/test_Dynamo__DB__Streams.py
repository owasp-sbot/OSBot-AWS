from osbot_aws.aws.dynamo_db.Dynamo_DB import Dynamo_DB
from osbot_aws.aws.dynamo_db.Dynamo_DB__Streams import Dynamo_DB__Streams
from osbot_aws.aws.dynamo_db.Dynamo_DB__Table import Dynamo_DB__Table
from osbot_aws.aws.dynamo_db.domains.DyDB__Table import DyDB__Table
from osbot_aws.testing.TestCase__Dynamo_DB import TestCase__Dynamo_DB
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import wait_for


class test_Dynamo__DB__Streams(TestCase__Dynamo_DB):

    dynamo_db_streams: Dynamo_DB__Streams
    dynamo_db_table  : DyDB__Table
    table_name       : str
    table_key_name   : str
    table_key_type   : str
    remove_on_exit   : bool = False

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.table_name        = 'temp-table-for-streams'
        cls.table_key_name         = 'an_key'
        cls.table_key_type         = 'S'
        table_kwargs = dict(dynamo_db  = cls.dynamo_db      ,
                            key_name   = cls.table_key_name ,
                            key_type   = cls.table_key_type ,
                            table_name = cls.table_name     )
        cls.dynamo_db_table = DyDB__Table(**table_kwargs)

        cls.dynamo_db_streams = Dynamo_DB__Streams(dynamo_db_table=cls.dynamo_db_table)
        #cls.dynamo_db_table.delete_table()
        #cls.dynamo_db_table.create_table()

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.remove_on_exit:
            cls.dynamo_db.table_delete(table_name=cls.table_name, wait_for_deletion=False)

    def test_setup(self):
        with self.dynamo_db_table as _:
            table_info = _.info()
            assert _.exists()                             is True
            assert table_info.get('AttributeDefinitions') ==  [{'AttributeName': self.table_key_name, 'AttributeType': self.table_key_type}]
            assert table_info.get('KeySchema'           ) ==  [{'AttributeName': self.table_key_name, 'KeyType'      : 'HASH'}]
            assert table_info.get('TableName'           ) == self.table_name


    # todo: finish adding streaming_support
    # def test_add_streaming_support(self):
    #     with self.dynamo_db_table as _:
    #         pprint(_.info())
    #         stream_view_type = 'NEW_IMAGE'
    #         stream_specification = { 'StreamEnabled'  : True            ,
    #                                  'StreamViewType': stream_view_type}
    #         #result = _.update_table(stream_specification)
    #         #pprint(result)
    #         from osbot_utils.utils.Misc import wait_for
    #         wait_for(0.2)


