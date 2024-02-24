from functools import cache

from botocore.exceptions import ClientError

from osbot_aws.apis.Session import Session
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.decorators.lists.group_by import group_by
from osbot_utils.decorators.lists.index_by import index_by
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.utils.Dev import pprint


class Bedrock(Kwargs_To_Self):
    region_name : str

    def __enter__(self                           ): return self
    def __exit__ (self, exc_type, exc_val, exc_tb): pass

    @cache_on_self
    def client(self):
        session = Session(region_name=self.region_name)
        return session.client('bedrock')

    @index_by
    @group_by
    def models(self):
        response = self.client().list_foundation_models()
        models   = response.get("modelSummaries")
        return models

    def models_active(self):
        models = {}
        for model in self.models():
            model_id = model.get("modelId")
            provider = model.get("providerName")
            output   = model.get('outputModalities').pop()   # note: assuming that there is only one output per model
            assert len(model_id.split( ".")) == 2

            status   = model.get('modelLifecycle').get('status')
            if status == 'ACTIVE':
                providers = models   [provider] = models   .get(provider, {})
                outputs   = providers[output  ] = providers.get(output  , {})
                outputs[model_id] = model
            # pprint(model)
            # break
        return models