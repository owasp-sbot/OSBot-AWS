from osbot_aws.aws.bedrock.models.amazon.Amazon_Titan_Tg1_Large import Amazon_Titan_Tg1_Large
from osbot_aws.testing.TestCase__Bedrock import TestCase__Bedrock


class test_Amazon_Titan_Tg1_Large(TestCase__Bedrock):

    def setUp(self):
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