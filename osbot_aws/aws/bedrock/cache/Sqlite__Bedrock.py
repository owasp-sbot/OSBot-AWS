from os import environ

from osbot_aws.aws.bedrock.cache.Sqlite__Bedrock__Row import Sqlite__Bedrock__Row
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.helpers.sqlite.Sqlite__Database import Sqlite__Database
from osbot_utils.utils.Files import current_temp_folder, path_combine

ENV_NAME_PATH_LOCAL_DBS        = 'PATH_LOCAL_DBS'
ENV_NAME_BEDROCK_DB_NAME       = 'BEDROCK_DB_NAME'
SQLITE_DB_NAME__SQLITE_BEDROCK = 'sqlite__bedrock.sqlite'
SQLITE_TABLE__BEDROCK_REQUESTS = 'bedrock_requests'


class Sqlite__Bedrock(Sqlite__Database):

    def __init__(self, db_path=None):
        super().__init__(db_path=db_path or self.path_sqlite_bedrock())
        self.setup()

    def path_db_folder(self):
        return environ.get(ENV_NAME_PATH_LOCAL_DBS) or current_temp_folder()

    def path_sqlite_bedrock(self):
        db_name = environ.get(ENV_NAME_BEDROCK_DB_NAME) or SQLITE_DB_NAME__SQLITE_BEDROCK
        return path_combine(self.path_db_folder(), db_name)

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