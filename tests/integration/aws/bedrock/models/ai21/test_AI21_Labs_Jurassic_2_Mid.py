from osbot_aws.aws.bedrock.models.ai21.AI21_Labs_Jurassic_2_Mid import AI21_Labs_Jurassic_2_Mid
from osbot_aws.testing.TestCase__Bedrock import TestCase__Bedrock
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set


class test_AI21_Labs_Jurassic_2_Mid(TestCase__Bedrock):

    def setUp(self) -> None:
        self.model = AI21_Labs_Jurassic_2_Mid()

    def test__init__(self):
        expected_vars = { 'max_tokens'     : 1024              ,
                          'model_id'       : 'ai21.j2-mid-v1'  ,
                          'prompt'         : ''                ,
                          'stop_sequences' : []                ,
                          'temperature'    : 0.0               ,
                          'top_p'          : 1.0               }
        assert self.model.__locals__() == expected_vars

    def test_model_invoke(self):
        #self.cache.disable()

        prompts           = ['hello',
                             'what is your model?',
                             'what is 40 + 2']
        current_prompt    = 2
        prompt            = prompts[current_prompt]
        self.model.prompt = prompt
        model_id  = self.model.model_id
        body      = self.model.body()

        response  = self.bedrock.model_invoke(model_id, body)

        #pprint(response)

        assert list_set(response) == ['completions', 'id', 'prompt']