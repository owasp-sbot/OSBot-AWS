# import pytest
# from decimal                                            import Decimal
# from osbot_aws.AWS_Config                               import AWS_Config
# from osbot_aws.aws.dynamo_db.Dynamo_DB__Table           import Dynamo_DB__Table
# from osbot_aws.aws.dynamo_db.domains.DyDB__Table        import DyDB__Table
# from osbot_aws.aws.dynamo_db.domains.DyDB__Timeseries   import DyDB__Timeseries, NAME_TIMESTAMP
# from osbot_utils.base_classes.Kwargs_To_Self            import Kwargs_To_Self
# from osbot_utils.utils.Dev                              import pprint
# from osbot_utils.utils.Misc                             import timestamp_utc_now, random_int, list_set, is_int, is_guid, wait_for, random_text
# from osbot_aws.testing.TestCase__Dynamo_DB              import TestCase__Dynamo_DB
# from osbot_utils.utils.Objects                          import base_types
#
#
# @pytest.mark.skip()
# class test_DyDB__Timeseries(TestCase__Dynamo_DB):
#     delete_on_exit  : bool             = False
#     dydb_timeseries : DyDB__Timeseries
#     table_name      : str              = 'pytest_db_timestamp'
#     account_id      : str
#     region_name     : str
#
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.dydb_timeseries           = DyDB__Timeseries(table_name=cls.table_name)
#         cls.dydb_timeseries.dynamo_db = cls.dynamo_db                               # set dydb_timeseries.dynamo_db to version of dynamo_db from TestCase__Dynamo_DB (which has the correct IAM permissions)
#         aws_config                    = AWS_Config()
#         cls.region_name               = aws_config.region_name()
#         cls.account_id                = aws_config.account_id()
#         cls.dydb_timeseries.create_table() # create if it doesn't exist
#
#     @classmethod
#     def tearDownClass(cls):
#         if cls.delete_on_exit:
#             assert cls.dydb_timeseries.delete_table(wait_for_deletion=False) is True
#
#     def test__init__(self):
#         assert self.region_name == 'eu-west-1'
#         expected_var = { 'dynamo_db'                : self.dynamo_db    ,
#                          'global_secondary_indexes' : []                ,
#                          'key_name'                 : 'id'              ,
#                          'key_type'                 : 'S'           ,
#                          'table_name'               : self.table_name   }
#         with self.dydb_timeseries as _:
#             assert _.__locals__() == expected_var
#             assert base_types(_) == [DyDB__Table, Dynamo_DB__Table, Kwargs_To_Self, object]
#
#
#     # def test_all_ids(self):
#     #     pprint(self.dydb_timeseries.all_ids())
#
#     # def test__clear_table(self):
#     #     result = self.dydb_timeseries.clear_table()
#     #     #pprint(result)
#
#
#     def test_delete_gsi(self):
#         with self.dydb_timeseries as _:
#             result = _.gsi_delete(index_name='string2')
#             pprint(result)
#
#     def test_delete_table(self):
#         with self.dydb_timeseries as _:
#             result = _.delete_table()
#             pprint(result)
#
#
#
#     def test_gsi_create(self):
#         with self.dydb_timeseries as _:
#             result        = _.gsi_create(index_name='string')
#             pprint(result)
#
#
#     # to wire up
#
#     def test_query_by_partition(self):
#         items           = self.dydb_timeseries.query_by_partition(self.partition)
#         assert len(items) > 0
#
#
#     def test_query_by_last_n_hours(self):
#         hours = 0.2
#         items = self.dydb_timeseries.query_by_last_n_hours(hours, partition=self.partition)
#         assert len(items) > 0
#         #pprint(items)
#
#     def test_query_by_timestamp(self):
#         hours = 1
#         start_timestamp = timestamp_utc_now() - (hours * 60 * 60 * 1000)            # get logs from last hour
#         end_timestamp   = timestamp_utc_now()
#
#         items = self.dydb_timeseries.query_by_timestamp(start_timestamp=start_timestamp, end_timestamp=end_timestamp, partition=self.partition)
#
#         assert len(items) > 0
#         # for index, item in enumerate(items):
#         #     timestamp = item.get('timestamp')
#         #     data      = item.get('data'     )
#         #     #assert list(data) == ['answer', 'another_key', 'and_another']
#         #     when = timestamp_to_datetime(timestamp)
#         #     #print(index, timestamp,when,  data)
#
#     # def test_info(self):
#     #     result = self.dydb_timeseries.info().get('data')
#     #     pprint(result)
#
#     @pytest.mark.skip(reason="FIX test to have valid data") # todo: fix test
#     def test_query_by_env_and_var(self):
#         query_var   = 'ip_address'
#         query_value = '35.205.163.48'  # Google's IP Address
#         env         = None
#         items       = self.dydb_timeseries.query_by_env_and_var(query_var, query_value, env)
#         assert len(items) > 0
