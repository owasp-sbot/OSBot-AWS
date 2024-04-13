from os import environ

from dotenv import load_dotenv

from osbot_utils.decorators.lists.group_by import group_by
from osbot_utils.decorators.lists.index_by import index_by
from osbot_utils.helpers.sqlite.domains.Sqlite__Cache__Requests import Sqlite__Cache__Requests
from osbot_utils.helpers.sqlite.domains.Sqlite__DB__Requests import Sqlite__DB__Requests
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Json                         import json_dumps, json_loads
from osbot_utils.utils.Lists                        import list_group_by
from osbot_utils.utils.Misc                         import str_sha256, timestamp_utc_now
from osbot_utils.utils.Str import str_dedent

ENV_NAME_BEDROCK_DB_NAME       = 'BEDROCK_DB_NAME'
SQLITE_DB_NAME__SQLITE_BEDROCK = 'sqlite__bedrock.sqlite'
SQLITE_TABLE__BEDROCK_REQUESTS = 'bedrock_requests'

class Bedrock__Cache(Sqlite__Cache__Requests):
    db_name        : str
    table_name     : str

    def __init__(self, db_path=None):
        load_dotenv()
        self.db_name    = environ.get(ENV_NAME_BEDROCK_DB_NAME) or SQLITE_DB_NAME__SQLITE_BEDROCK
        self.table_name = SQLITE_TABLE__BEDROCK_REQUESTS
        super().__init__(db_path=db_path, db_name=self.db_name, table_name=self.table_name)











    def comments(self, model):
        model_id = model.model_id
        body     = model.body()
        return self.cache_entry_comments(model_id, body)

    def comments_print(self, model):
        model_id = model.model_id
        body     = model.body()
        print()
        print()
        with_prompt = ""
        if hasattr(model, 'text_prompts'):
            with_prompt = "with prompt     : {model.text_prompts}\n"

        print(str_dedent(f"""
                ----------------------------
                comment on model: {model_id} "
                {with_prompt}            
                {self.cache_entry_comments(model_id, body)}"""))

    def comments_set(self, model, new_comments):
        model_id = model.model_id
        body     = model.body()
        return self.cache_entry_comments_update(model_id=model_id, body=body, new_comments=new_comments)

    # Bedrock overwrite methods

    def model_invoke(self, bedrock, model_id, body):
        target           = bedrock.model_invoke
        target_kwargs    = {'model_id': model_id, 'body': body}
        return self.invoke_with_cache(target, target_kwargs)


    def model_invoke_stream(self,bedrock, model_id, body):
        def capture_chunks():
            response = bedrock.model_invoke_stream(model_id, body)
            chunks   = []
            for chunk in response:
                chunks.append(chunk)
            return chunks

        target           = capture_chunks
        target_kwargs    = {}
        request_data     = dict(model_id=model_id, body=body, mode='invoke_stream')
        return self.invoke_with_cache(target, target_kwargs, request_data)


    @index_by
    @group_by
    def models(self, bedrock):                          # todo refactor out the caching login with this and model_invoke methods
        target           = bedrock.models
        target_kwargs    = {}
        request_data     = dict(method='models')
        return self.invoke_with_cache(target, target_kwargs, request_data)


