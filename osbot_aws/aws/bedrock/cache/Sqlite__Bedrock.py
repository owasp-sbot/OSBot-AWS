from osbot_aws.aws.bedrock.cache.Sqlite__Bedrock__Row import Sqlite__Bedrock__Row
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.helpers.sqlite.Sqlite__Database import Sqlite__Database

PATH_FILE__SQLITE_BEDROCK      = '/tmp/sqlite__bedrock.db'             # todo: find a better location for this cache
SQLITE_TABLE__BEDROCK_REQUESTS = 'bedrock_requests'


class Sqlite__Bedrock(Sqlite__Database):

    def __init__(self, db_path=None):
        super().__init__(db_path=db_path or self.path_sqlite_bedrock())
        self.setup()

    def path_sqlite_bedrock(self):
        return PATH_FILE__SQLITE_BEDROCK

    @cache_on_self
    def table_requests(self):
        return self.table(SQLITE_TABLE__BEDROCK_REQUESTS)

    def table_requests__create(self):
        with self.table_requests() as _:
            _.row_schema = Sqlite__Bedrock__Row                    # set the table_class
            if _.exists() is False:
                _.create()                                          # create if it doesn't exist
                _.index_create('request_hash')                      # add index to the request_hash field
                return True
        return False

    def table_requests__reset(self):
        self.table_requests().delete()
        return self.table_requests__create()

    def setup(self):
        self.table_requests__create()
        return self