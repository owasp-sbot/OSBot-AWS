from osbot_utils.decorators.methods.cache import cache

from osbot_aws.apis.Session import Session

class Kinesis:

    @cache
    def kinesis(self):
        return Session().client('kinesis')

    def streams(self):
        return self.kinesis().list_streams()
