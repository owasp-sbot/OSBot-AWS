from unittest import TestCase

from osbot_aws.aws.bedrock.models.anthropic.Anthropic__Claude_Instant_V1 import Anthropic__Claude_Instant_V1
from osbot_utils.utils.Dev import pprint


class test_Anthropic__Claude_Instant_V1(TestCase):

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