from osbot_aws.aws.bedrock.models.anthropic.Anthropic__Claude_Messages_API import Anthropic__Claude_Messages_API
from osbot_aws.testing.TestCase__Bedrock import TestCase__Bedrock


class test_Anthropic__Claude_Messages_API(TestCase__Bedrock):

    def setUp(self) -> None:
        self.model_id = 'anthropic.claude-3-haiku-20240307-v1:0'
        self.model    = Anthropic__Claude_Messages_API(model_id=self.model_id)


    def test__init__(self):
        expected_vars = { 'anthropic_version'   : 'bedrock-2023-05-31'       ,
                          'max_tokens'          : 1024                       ,
                          'messages'            : []                         ,
                          'model_id'            : self.model_id              ,
                          'stop_sequences'      : []                         ,
                          'system'              : ''                         ,
                          'temperature'         : 0.0                        ,
                          'top_k'               : 0                          ,
                          'top_p'               : 1                          }
        assert self.model.__locals__() == expected_vars