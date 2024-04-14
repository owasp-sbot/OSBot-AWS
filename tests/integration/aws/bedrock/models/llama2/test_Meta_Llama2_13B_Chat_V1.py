from osbot_aws.aws.bedrock.models.ai21.AI21_Labs_Jurassic_2_Mid import AI21_Labs_Jurassic_2_Mid
from osbot_aws.aws.bedrock.models.llama2.Meta_Llama2_13b_chat_v1 import Meta_Llama2_13B_Chat_V1
from osbot_aws.aws.boto3.Capture_Boto3_Error import capture_boto3_error
from osbot_aws.testing.TestCase__Bedrock import TestCase__Bedrock
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set


class test_Meta_Llama2_13B_Chat_V1(TestCase__Bedrock):

    def setUp(self) -> None:
        self.model = Meta_Llama2_13B_Chat_V1()

    def test__init__(self):
        expected_vars = { 'max_gen_len'    : 1024                     ,
                          'model_id'       : 'meta.llama2-13b-chat-v1',
                          'prompt'         : ''                       ,
                          'temperature'    : 0.0                      ,
                          'top_p'          : 1.0                      }
        assert self.model.__locals__() == expected_vars

    @capture_boto3_error
    def test_model_invoke(self):
        #self.cache.disable()

        prompts           = ['hello',                                       # this provided a very weird result , containing code
                             'what is your model?',                         # this also provided a weird result, containing some code
                             'what is 40 + 2',                              # this got the numbers wrong, it refereed to: 40 + 20 = 60
                             'What is the average lifespan of a Llama?'     # this was good, which was the question from https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-meta.html
                             ]
        current_prompt    = 2
        prompt            = prompts[current_prompt]
        self.model.prompt = prompt
        model_id  = self.model.model_id
        body      = self.model.body()

        response  = self.bedrock.model_invoke(model_id, body)

        #pprint(response)

        assert list_set(response) == ['generation', 'generation_token_count', 'prompt_token_count', 'stop_reason']