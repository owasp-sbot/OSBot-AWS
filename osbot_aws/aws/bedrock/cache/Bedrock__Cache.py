from osbot_aws.aws.bedrock.cache.Sqlite__Bedrock import Sqlite__Bedrock
from osbot_aws.aws.bedrock.cache.Sqlite__Bedrock__Row import Sqlite__Bedrock__Row__Type
from osbot_utils.base_classes.Kwargs_To_Self      import Kwargs_To_Self
from osbot_utils.utils.Dev                        import pprint
from osbot_utils.utils.Json import json_dumps
from osbot_utils.utils.Misc import str_sha256


class Bedrock__Cache(Kwargs_To_Self):
    enabled        : bool            = True
    sqlite_bedrock : Sqlite__Bedrock = None

    def __init__(self, db_path=None):
        super().__init__()
        self.sqlite_bedrock = Sqlite__Bedrock(db_path=db_path)

    def cache_add(self, request_data, response_data, request_type : Sqlite__Bedrock__Row__Type):
        new_row = self.cache_table().new_row_obj()
        new_row.request_data  = json_dumps(request_data)
        new_row.request_hash  = str_sha256(new_row.request_data)
        new_row.response_data = json_dumps(response_data)
        new_row.response_hash = str_sha256(new_row.response_data)
        new_row.record_type   = request_type
        if self.cache_table().row_add(new_row).get('status') == 'ok':
            self.cache_table().commit()
        return new_row


    def cache_table(self):
        return self.sqlite_bedrock.table_requests()

    def model_invoke(self, bedrock, model_id, body):
        pprint('------- in  Bedrock__Cache ------ ')
        # pprint(model_id)
        # pprint(json_md5(body))
        # pprint(body)
        return bedrock.model_invoke(model_id, body)

