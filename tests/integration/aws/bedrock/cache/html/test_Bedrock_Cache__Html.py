from unittest import TestCase

from osbot_aws.aws.bedrock.cache.Bedrock__Cache              import Bedrock__Cache, SQLITE_TABLE__BEDROCK_REQUESTS
from osbot_aws.aws.bedrock.cache.html.Bedrock_Cache__Html    import Bedrock_Cache__Html
from osbot_utils.helpers.sqlite.cache.Cache__Table           import Cache__Table
from osbot_utils.helpers.sqlite.cache.Sqlite__Cache__Requests__Table import Sqlite__Cache__Requests__Table
from osbot_utils.utils.Files                                 import file_name


class test_Bedrock_Cache__Html(TestCase):

    def setUp(self):
        self.bedrock_cache = Bedrock_Cache__Html()

    def test___init__(self):
        assert type(self.bedrock_cache.table)      is Sqlite__Cache__Requests__Table
        assert self.bedrock_cache.table.table_name == SQLITE_TABLE__BEDROCK_REQUESTS
        assert self.bedrock_cache.target_file      == '/tmp/tmp-bedrock-cache.html'
        assert self.bedrock_cache.title            == 'Html Page with Bedrock_Cache_Data'
        assert self.bedrock_cache.sub_title        == '....'
        assert self.bedrock_cache.row_elements     == []

        with self.bedrock_cache.cache as _:
            sqlite_requests = _.sqlite_requests
            assert type(_)                           is Bedrock__Cache
            assert file_name(sqlite_requests.db_path) == _.db_name