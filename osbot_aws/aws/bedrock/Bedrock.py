from functools import cache

from botocore.exceptions import ClientError

from osbot_aws.apis.Session import Session
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.decorators.lists.group_by import group_by
from osbot_utils.decorators.lists.index_by import index_by
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Json import json_dumps, json_loads


class Bedrock(Kwargs_To_Self):
    region_name : str

    def __enter__(self                           ): return self
    def __exit__ (self, exc_type, exc_val, exc_tb): pass

    @cache_on_self
    def client(self):
        session = Session(region_name=self.region_name)
        return session.client('bedrock')

    def model(self, model_id):
        return self.models__by_id().get(model_id)

    def model_invoke(self, model_id, body):
        body_as_str = json_dumps(body)
        accept      = 'application/json'
        contentType = 'application/json'

        response = self.runtime().invoke_model(body=body_as_str, modelId=model_id, accept=accept, contentType=contentType)
        response_body = json_loads(response.get('body').read())
        return response_body

    def model_invoke_stream(self, model_id, body):
        body_as_str = json_dumps(body)
        accept      = 'application/json'
        contentType = 'application/json'

        response = self.runtime().invoke_model_with_response_stream(body=body_as_str, modelId=model_id, accept=accept, contentType=contentType)

        stream   = response.get('body')
        if stream:
            for event in stream:
                chunk = event.get('chunk')
                if chunk:
                    data = json_loads(chunk.get('bytes').decode())
                    yield data

    @index_by
    @group_by
    def models(self):
        response = self.client().list_foundation_models()
        models   = response.get("modelSummaries")
        return models

    @cache_on_self
    def models_active(self):
        models = {}
        for model in self.models():
            model_id   = model.get("modelId"                )
            provider   = model.get("providerName"           )
            for output in model.get('outputModalities'       ):
                for throughput in model.get('inferenceTypesSupported'):
                    status   = model.get('modelLifecycle').get('status')
                    if status == 'ACTIVE':
                        throughputs = models      [throughput] = models     .get(throughput, {})
                        providers   = throughputs [provider  ] = throughputs.get(provider  , {})
                        outputs     = providers   [output    ] = providers  .get(output    , {})
                        outputs[model_id] = model
        return models

    @cache_on_self
    def models__by_id(self):
        return self.models(index_by='modelId')

    def models_by_throughput(self, throughput_mode):
        models_active = self.models_active()
        models        = {}
        tree  = models_active.get(throughput_mode, {})
        for provider in tree.values():
            for _, outputs in provider.items():
                for model_id, model in outputs.items():
                    models[model_id] = model
        return models

    def models_by_throughput__on_demand(self):
        return self.models_by_throughput('ON_DEMAND')

    def models_by_throughput__provisioned(self):
        return self.models_by_throughput('PROVISIONED')

    @cache_on_self
    def runtime(self):
        session = Session(region_name=self.region_name)
        return session.client('bedrock-runtime')