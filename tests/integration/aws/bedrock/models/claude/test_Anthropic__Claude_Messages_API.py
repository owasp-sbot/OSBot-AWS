from osbot_aws.aws.bedrock.models.claude.Anthropic__Claude_Messages_API import Anthropic__Claude_Messages_API
from osbot_aws.aws.boto3.Capture_Boto3_Error import capture_boto3_error
from osbot_aws.testing.TestCase__Bedrock import TestCase__Bedrock
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set


class test_Anthropic__Claude_Messages_API(TestCase__Bedrock):

    def setUp(self) -> None:
        self.model    = Anthropic__Claude_Messages_API()


    def test__init__(self):
        expected_vars = { 'anthropic_version'   : 'bedrock-2023-05-31'       ,
                          'max_tokens'          : 1024                       ,
                          'messages'            : []                         ,
                          'model_id'            : ''                         ,
                          'stop_sequences'      : []                         ,
                          'temperature'         : 0.0                        ,
                          'top_k'               : 0                          ,
                          'top_p'               : 1                          }
        assert self.model.__locals__() == expected_vars

    def with_model_call_prompt(self, model_id, prompt_index):
        self.model.model_id = model_id
        prompts        = ['hello',
                          'what is your model?',
                          'what is 40 + 2']
        system         = 'Respond with text and lots of emojis'
        messages       = [{"role": "user", "content": prompts[prompt_index]}]

        model_id         = self.model.model_id
        body             = self.model.body(messages, system)
        response         = self.bedrock.model_invoke(model_id, body)
        #pprint(response)
        assert list_set(response) == ['content', 'id', 'model', 'role', 'stop_reason', 'stop_sequence', 'type', 'usage']
        return response.get('content')

    @capture_boto3_error
    def test_model_invoke(self):
        #self.cache.disable()
        models_ids = ['anthropic.claude-3-haiku-20240307-v1:0', 'anthropic.claude-3-sonnet-20240229-v1:0',
                      'anthropic.claude-instant-v1','anthropic.claude-v2', 'anthropic.claude-v2:1']

        #print()
        for model_id in models_ids:
            #print(f'\n *** {model_id} ***')
            for index in range(0,3):
                content  = self.with_model_call_prompt(model_id,index)
                assert len(content) == 1
                assert list_set(content[0]) == ['text', 'type']



        #assert body               == expected_body
        #assert list_set(response) == list_set(expected_response)