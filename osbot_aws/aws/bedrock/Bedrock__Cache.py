from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.helpers.sqlite.Sqlite__Database import Sqlite__Database
from osbot_utils.utils.Dev                   import pprint

PATH_FILE__SQLITE_BEDROCK      = '/tmp/sqlite__bedrock.db'             # todo: find a better location for this cache
SQLITE_TABLE__BEDROCK_REQUESTS = 'bedrock_requests'

class Sqlite__Bedrock__Row(Kwargs_To_Self):
    request_hash  : str
    request_data  : str
    response_hash : str
    response_data : str
    cache_hits    : int
    timestamp     : int
    latest        : bool


class Sqlite__Bedrock(Sqlite__Database):

    def __init__(self):
        db_path = self.path_sqlite_bedrock()
        super().__init__(db_path=db_path)
        self.setup()

    def path_sqlite_bedrock(self):
        return PATH_FILE__SQLITE_BEDROCK

    def table_requests(self):
        return self.table(SQLITE_TABLE__BEDROCK_REQUESTS)

    def setup(self):

        with self.table_requests() as _:
            print('----')
            print(_.exists())
            print('inside table_requests')
            _.print()
        return self


class Bedrock__Cache(Kwargs_To_Self):
    enabled        : bool            = True
    sqlite_bedrock : Sqlite__Bedrock


    def model_invoke(self, bedrock, model_id, body):
        pprint('------- in  Bedrock__Cache ------ ')
        # pprint(model_id)
        # pprint(json_md5(body))
        # pprint(body)
        return bedrock.model_invoke(model_id, body)

