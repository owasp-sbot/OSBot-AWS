import pytest

from osbot_aws.aws.bedrock.models.mistral.Mistral_AI_7b_Instruct_v0_2 import Mistral_AI_7b_Instruct_v0_2
from osbot_aws.aws.boto3.Capture_Boto3_Error import capture_boto3_error
from osbot_aws.testing.TestCase__Bedrock import TestCase__Bedrock
from osbot_utils.utils.Misc import list_set, in_github_action


class test_Mistral_AI_7b_Instruct_v0_2(TestCase__Bedrock):

    def setUp(self) -> None:
        if in_github_action():                                  # disabling Bedrock tests in GitHub actions since they are not 100% deterministic
            pytest.skip()
        self.model = Mistral_AI_7b_Instruct_v0_2()

    def test__init__(self):
        expected_vars = { 'max_tokens'     : 1024                                ,
                          'model_id'       : 'mistral.mistral-7b-instruct-v0:2'  ,
                          'prompt'         : ''                                  ,
                          'stop'           : []                                  ,
                          'temperature'    : 0.0                                 ,
                          'top_k'          : 1                                   ,
                          'top_p'          : 1.0                                 }
        assert self.model.__locals__() == expected_vars

    @capture_boto3_error
    def test_model_invoke(self):
        #self.cache.disable()

        prompts           = ['hello'                                                                ,       # without mistral prompt formatting
                             'what is your model?'                                                  ,       #    providing direct questions
                             'what is 40 + 2'                                                       ,       #    results in weird completion results
                             '<s>[INST] What is your favourite condiment? [/INST]'                  ,       # with this <s>[INST] format we get good answers
                             """<s>[INST] In Bash, how do I list all text files in                          
                                          the current directory (excluding subdirectories)      
                                          that have been modified in the last month? [/INST]"""
                             ]
        current_prompt    = 0
        prompt            = prompts[current_prompt]

        self.model.prompt = prompt
        model_id  = self.model.model_id
        body      = self.model.body()

        response  = self.bedrock.model_invoke(model_id, body)

        #pprint(response)

        assert list_set(response) == ['outputs']