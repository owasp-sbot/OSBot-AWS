import boto3

from osbot_aws.apis.Session import Session
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.decorators.methods.remove_return_value import remove_return_value
from osbot_utils.utils.Json import to_json_str


class API_Gateway_Management_API:

    def __init__(self, endpoint_url):
        self.endpoint_url = endpoint_url
    def __enter__(self                           ): return self
    def __exit__ (self, exc_type, exc_val, exc_tb): pass


    @cache_on_self
    def client(self):
        return boto3.client('apigatewaymanagementapi', endpoint_url=self.endpoint_url)

    @remove_return_value(field_name='ResponseMetadata')
    def connection(self, connection_id):
        return self.client().get_connection(ConnectionId=connection_id)

    def post_to_connection(self, connection_id, data):
        if type(data) is dict:
            data = to_json_str(data)
        return self.client().post_to_connection(ConnectionId=connection_id, Data=data)