from osbot_aws.apis.Session                             import Session
from osbot_utils.decorators.lists.group_by              import group_by
from osbot_utils.decorators.lists.index_by              import index_by
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from osbot_utils.decorators.methods.remove_return_value import remove_return_value

class API_Gateway_V2:

    def __enter__(self                           ): return self
    def __exit__ (self, exc_type, exc_val, exc_tb): pass


    @cache_on_self
    def client(self):
        return Session().client('apigatewayv2')

    @remove_return_value(field_name='ResponseMetadata')
    def api(self, api_id):
        return self.client().get_api(ApiId=api_id)

    @group_by
    @index_by
    def apis(self):
        return self.client().get_apis().get('Items')

    def apis_by_name(self):
        return self.apis(index_by='Name')
