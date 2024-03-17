from unittest import TestCase

from osbot_aws.aws.bedrock.Bedrock__Cache import Bedrock__Cache
from osbot_utils.helpers.trace.Trace_Call import trace_calls
from osbot_utils.testing.Duration import Duration
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Json import json_sha_256


class test_Bedrock__Cache(TestCase):

    def setUp(self):
        pass

    @trace_calls(ignore         = []    , include        = ['osbot_'], contains=[]                 ,
                 source_code    = False , show_lines     = False ,
                 show_duration  = True , duration_bigger_than = 0.001,
                 show_class     = True , show_locals    = False ,
                 show_types     = False  , show_internals = True , extra_data = False          ,
                 show_types_padding = 100  , duration_padding=120,
                 enabled        = False  )
    def test_check_duration(self):
        # with Duration() as duration:
        self.bedrock_cache = Bedrock__Cache()

        #self.sqlite_bedrock = self.bedrock_cache.sqlite_bedrock
        # pprint(duration.milliseconds())







        return
        # database = self.sqlite_bedrock
        # pprint(self.sqlite_bedrock.exists())
        # pprint(database.in_memory)
        # pprint(database.tables())
        #
        # print(json_sha_256({'a'}))
        #path_temp_database = self.database.path_temp_database()

