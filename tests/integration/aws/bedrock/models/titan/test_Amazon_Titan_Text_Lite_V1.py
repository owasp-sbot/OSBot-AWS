import pytest

from osbot_aws.aws.bedrock.models.titan.Amazon_Titan_Text_Lite_V1 import Amazon_Titan_Text_Lite_V1
from osbot_aws.testing.TestCase__Bedrock                          import TestCase__Bedrock
from osbot_utils.utils.Env                                        import in_github_action


class test_Amazon_Titan_Text_Lite_V1(TestCase__Bedrock):

    def setUp(self):
        if in_github_action():                                  # disabling Bedrock tests in GitHub actions since they are not 100% deterministic
            pytest.skip()
        self.model    = Amazon_Titan_Text_Lite_V1()
        self.model_id = 'amazon.titan-text-lite-v1'

    def test__init__(self):
        expected_vars = {'input_text'       : ''            ,
                         'max_token_count'  :  1024         ,
                         'model_id'         : self.model_id ,
                         'stop_sequences'   : []            ,
                         'temperature'      : 0.0           ,
                         'topP'             : 1             }
        assert self.model.__locals__() == expected_vars

    #@cache_bedrock_response
    #@print_boto3_calls()
    def test_model_invoke(self):
        #self.cache.force_request = True
        prompt = "Hello"
        expected_response  = { 'inputTextTokenCount': 3,
                               'results'            : [ { 'completionReason': 'FINISH'                           ,
                                                          'outputText'      : '\n\nBot: Hello! How can I help you?',
                                                          'tokenCount'      : 12                                 }]}
        self.model.input_text = prompt
        model_id  = self.model.model_id
        body      = self.model.body()
        response  = self.bedrock.model_invoke(model_id, body)
        assert response == expected_response

        #response = self.bedrock.model_invoke(model_id, body)
        #pprint(response)