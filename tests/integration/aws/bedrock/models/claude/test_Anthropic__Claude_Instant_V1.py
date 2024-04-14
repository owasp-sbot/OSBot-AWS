from unittest import TestCase

from osbot_aws.aws.bedrock.models.claude.Anthropic__Claude_Instant_V1 import Anthropic__Claude_Instant_V1
from osbot_aws.testing.TestCase__Bedrock import TestCase__Bedrock
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set


class test_Anthropic__Claude_Instant_V1(TestCase__Bedrock):

    def setUp(self) -> None:
        self.model = Anthropic__Claude_Instant_V1()

    def test__init__(self):
        expected_vars = { 'max_tokens_to_sample': 1024                              ,
                          'model_id'            : 'anthropic.claude-instant-v1'     ,
                          'prompt'              : ''                                ,
                          'prompt_format'       : '\n\nHuman:{prompt}\n\nAssistant:',
                          'stop_sequences'      : []                                ,
                          'temperature'         : 0.0                               ,
                          'top_k'               : 0                                 ,
                          'top_p'               : 1                                 }
        assert self.model.__locals__() == expected_vars

    def test_model_invoke(self):
        #self.cache.disable()
        #self.cache.force_request = True
        prompts        = ['hello',
                          'what is your model?',
                          'what is 40 + 2']
        current_prompt = 2
        prompt         = prompts[current_prompt]
        expected_body      = { 'max_tokens_to_sample': 1024
            ,
                               'prompt'              : f'\n\nHuman:{prompt}\n\nAssistant:',
                               'stop_sequences'      : []   ,
                               'temperature'         : 0.0  ,
                               'top_k'               : 0    ,
                               'top_p'               : 1    }
        expected_response  = {'completion': ' Hello!', 'stop': '\n\nHuman:', 'stop_reason': 'stop_sequence'}
        self.model.prompt = prompt
        model_id  = self.model.model_id
        body      = self.model.body()

        response  = self.bedrock.model_invoke(model_id, body)


        assert body               == expected_body
        assert list_set(response) == list_set(expected_response)