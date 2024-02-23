from functools import cache

from botocore.exceptions import ClientError

from osbot_aws.apis.Session import Session
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.decorators.methods.cache_on_self import cache_on_self


class Bedrock(Kwargs_To_Self):
    region_name : str

    def __enter__(self                           ): return self
    def __exit__ (self, exc_type, exc_val, exc_tb): pass

    @cache_on_self
    def client(self):
        session = Session(region_name=self.region_name)
        return session.client('bedrock')

    def models(self):
        response = self.client().list_foundation_models()
        return response
        models = response["modelSummaries"]
        return models
