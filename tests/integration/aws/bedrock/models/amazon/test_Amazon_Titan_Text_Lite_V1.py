from osbot_aws.aws.bedrock.models.amazon.Amazon_Titan_Text_Lite_V1 import Amazon_Titan_Text_Lite_V1
from osbot_aws.aws.boto3.View_Boto3_Rest_Calls import print_boto3_calls
from osbot_aws.testing.TestCase__Bedrock import TestCase__Bedrock

from unittest.mock import patch
import functools

# Cache for storing responses
bedrock_response_cache = {}


def cache_bedrock_response(func):
    @functools.wraps(func)
    def wrapper_cache(*args, **kwargs):
        self = args[0]  # The instance of the test class
        cache_key = (self.model.model_id, self.model.input_text)

        if cache_key in bedrock_response_cache:
            print("Using cached response for:", cache_key)
            return bedrock_response_cache[cache_key]

        # Save the original 'model_invoke' method
        original_method = self.bedrock.model_invoke

        # Define a side_effect function that calls the original method
        # and caches its response
        def side_effect(*args, **kwargs):
            # Use the original method to get the response
            response = original_method(*args, **kwargs)
            # Cache the response
            bedrock_response_cache[cache_key] = response
            return response

        # Patch the 'model_invoke' method with our side_effect
        with patch.object(self.bedrock, 'model_invoke', side_effect=side_effect):
            return func(*args, **kwargs)

    return wrapper_cache


class test_Amazon_Titan_Text_Lite_V1(TestCase__Bedrock):

    def setUp(self):
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
    @print_boto3_calls()
    def test_model_invoke(self):
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