from osbot_aws.aws.bedrock.cache.Sqlite__Bedrock    import Sqlite__Bedrock
from osbot_utils.base_classes.Kwargs_To_Self        import Kwargs_To_Self
from osbot_utils.utils.Json                         import json_dumps, json_loads
from osbot_utils.utils.Lists                        import list_group_by
from osbot_utils.utils.Misc                         import str_sha256


class Bedrock__Cache(Kwargs_To_Self):
    enabled        : bool            = True
    sqlite_bedrock : Sqlite__Bedrock = None

    def __init__(self, db_path=None):
        super().__init__()
        self.sqlite_bedrock = Sqlite__Bedrock(db_path=db_path)

    def cache_add(self, request_data, response_data):
        new_row_obj = self.create_new_cache_obj(request_data, response_data)
        return self.cache_table().row_add_and_commit(new_row_obj)

    def cache_entries(self):
        return self.cache_table().rows()

    def cache_entry(self, request_data):
        request_data        = json_dumps(request_data)
        request_data_sha256 = str_sha256(request_data)
        data                = self.cache_table().select_rows_where(request_hash=request_data_sha256)
        if len(data) > 0:                       # todo: add logic to handle (or log), where there are multiple entries with the same hash
            return data[0]
        return {}

    def cache_table(self):
        return self.sqlite_bedrock.table_requests()

    def cache_request_data(self, model_id, body):
        request_data = dict(model        = model_id     ,
                            body         = body         )
        return request_data

    def create_new_cache_data(self, request_data, response_data):
        request_data_json  = json_dumps(request_data)
        request_data_hash  = str_sha256(request_data_json)
        response_data_json = json_dumps(response_data)
        response_data_hash = str_sha256(response_data_json)
        return dict(request_data  = request_data_json   ,
                    request_hash  = request_data_hash   ,
                    response_data = response_data_json  ,
                    response_hash = response_data_hash  )

    def create_new_cache_obj(self, request_data, response_data):
        new_row_data = self.create_new_cache_data(request_data, response_data)
        new_row_obj = self.cache_table().new_row_obj(new_row_data)
        return new_row_obj



    def delete_where_request_data(self, request_data):                                      # todo: check if it is ok to use the request_data as a query target, or if we should use the request_hash variable
        if type(request_data) is dict:                                                      # if we get an request_data obj
            request_data = json_dumps(request_data)                                         # convert it to the json dump
        if type(request_data) is str:                                                       # make sure we have a string
            if len(self.rows_where__request_data(request_data)) > 0:                        # make sure there is at least one entry to delete
                self.cache_table().rows_delete_where(request_data=request_data)             # delete it
                return len(self.rows_where__request_data(request_data)) == 0                # confirm it was deleted
        return False                                                                        # if anthing was not right, return False

    def disable(self):
        self.enabled = False
        return self

    def requests_data__all(self):
        requests_data = []
        for row in self.cache_table().rows():
            request_data     = row.get('request_data')
            request_hash     = row.get('request_hash')
            request_data_obj = json_loads(request_data)
            request_data_obj['_hash'] = request_hash
            requests_data.append(request_data_obj)
        return requests_data

    def requests_data__by_model_id(self):
        values        = self.requests_data__all()
        group_by      = 'model'
        requests_data = list_group_by(values=values, group_by=group_by)
        if 'None' in requests_data:                         # if there are other entries in the cache
            del requests_data['None']                       # don't include them
        return requests_data

    def requests_data__with_model_id(self, model_id):
        return self.requests_data__by_model_id().get(model_id, [])


    def rows_where(self, **kwargs):
        return self.cache_table().select_rows_where(**kwargs)

    def rows_where__request_data(self, request_data):
        return self.rows_where(request_data=request_data)

    def rows_where__request_hash(self, request_hash):
        return self.rows_where(request_hash=request_hash)

    # CACHED methods

    def model_invoke(self, bedrock, model_id, body):
        if self.enabled is False:
            return bedrock.model_invoke(model_id, body)
        request_data  = self.cache_request_data(model_id, body)
        cache_entry   = self.cache_entry(request_data)
        if cache_entry:
            response_data_json = cache_entry.get('response_data')
            if response_data_json:
                return json_loads(response_data_json)
        response_data = bedrock.model_invoke(model_id, body)
        self.cache_add(request_data=request_data, response_data=response_data)
        return response_data

    def models(self, bedrock):
        if self.enabled is False:
            return bedrock.models()
        request_data = dict(method='models')
        cache_entry  = self.cache_entry(request_data)
        if cache_entry:
            response_data_json = cache_entry.get('response_data')
            if response_data_json:
                return json_loads(response_data_json)
        response_data = bedrock.models()
        self.cache_add(request_data=request_data, response_data=response_data)
        return response_data

