import pytest

from osbot_aws.aws.bedrock.cache.Bedrock__Cache                 import Bedrock__Cache
from osbot_aws.aws.bedrock.models.titan.Amazon_Titan_Tg1_Large  import Amazon_Titan_Tg1_Large
from osbot_aws.testing.TestCase__Bedrock                        import TestCase__Bedrock
from osbot_utils.utils.Json                                     import json_parse
from osbot_utils.utils.Env                                      import in_github_action
from osbot_utils.utils.Misc                                     import list_set


class test_Amazon_Titan_Tg1_Large(TestCase__Bedrock):

    def setUp(self):
        if in_github_action():                                  # disabling Bedrock tests in GitHub actions since they are not 100% deterministic
            pytest.skip()
        self.model    = Amazon_Titan_Tg1_Large()
        self.model_id = 'amazon.titan-tg1-large'

    def test__init__(self):
        expected_vars = {'input_text'       : ''            ,
                         'max_token_count'  :  1024         ,
                         'model_id'         : self.model_id ,
                         'stop_sequences'   : []            ,
                         'temperature'      : 0.0           ,
                         'topP'             : 1             }
        assert self.model.__locals__() == expected_vars

    def test_model_invoke(self):
        prompt = "Hello"
        expected_response  = { 'inputTextTokenCount': 3,
                               'results'            : [ { 'completionReason': 'FINISH'                           ,
                                                          'outputText'      : '\nBot: Hello! How can I help you?',
                                                          'tokenCount'      : 11                                 }]}
        self.model.input_text = prompt
        model_id  = self.model.model_id
        body      = self.model.body()
        response  = self.bedrock.model_invoke(model_id, body)
        assert response == expected_response

        #@trace_calls(ignore=[], include=['osbot_'], contains=[])
    def test__check_bedrock_behaviour(self):
        bedrock_cache: Bedrock__Cache
        bedrock_cache   = self.bedrock.bedrock_cache
        prompt          = 'hello'
        model_id        = self.model_id
        body            = self.model.body(prompt)
        request_data    = bedrock_cache.cache_request_data(model_id, body)
        direct_response = self.bedrock.model_invoke(model_id, body)
        cache_entry     = bedrock_cache.cache_entry(request_data)
        assert list_set(direct_response)    == ['inputTextTokenCount', 'results']
        assert direct_response              == json_parse(cache_entry.get('response_data'))         # confirm data we received matched the data in the cache



