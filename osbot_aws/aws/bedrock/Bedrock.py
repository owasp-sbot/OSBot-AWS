from functools import cache

from osbot_aws.apis.Session import Session


class Bedrock:

    def __enter__(self                           ): return self
    def __exit__ (self, exc_type, exc_val, exc_tb): pass

    @cache
    def client(self):
        return Session().client('bedrock')
