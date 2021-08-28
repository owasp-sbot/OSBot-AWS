from osbot_utils.decorators.methods.cache import cache
from osbot_utils.decorators.methods.cache_on_self import cache_on_self

from osbot_aws.apis.Session import Session

class Kinesis:

    @cache_on_self
    def kinesis(self):
        return Session().client('kinesis')

    def streams(self):
        return self.kinesis().list_streams()
