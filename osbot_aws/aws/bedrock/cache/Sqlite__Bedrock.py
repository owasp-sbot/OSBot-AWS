from os import environ

from osbot_aws.aws.bedrock.cache.Sqlite__Bedrock__Row import Sqlite__Bedrock__Row
from osbot_utils.helpers.sqlite.domains.Sqlite__DB__Local import Sqlite__DB__Local
from osbot_utils.helpers.sqlite.domains.Sqlite__DB__Requests import Sqlite__DB__Requests

ENV_NAME_BEDROCK_DB_NAME       = 'BEDROCK_DB_NAME'
SQLITE_DB_NAME__SQLITE_BEDROCK = 'sqlite__bedrock.sqlite'
SQLITE_TABLE__BEDROCK_REQUESTS = 'bedrock_requests'


class Sqlite__Bedrock(Sqlite__DB__Requests):
    db_name     : str
    table_name  : str
    table_schema: type

    def __init__(self,db_path=None):
        self.db_name     = environ.get(ENV_NAME_BEDROCK_DB_NAME) or SQLITE_DB_NAME__SQLITE_BEDROCK
        #self.table_name  = SQLITE_TABLE__BEDROCK_REQUESTS
        #self.table_schema = Sqlite__Bedrock__Row
        super().__init__(db_path=db_path)
