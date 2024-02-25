from unittest import TestCase

from osbot_aws.aws.bedrock.models.amazon.Amazon_Titan_Text_Express_V1 import Amazon_Titan_Text_Express_V1
from osbot_aws.aws.boto3.Capture_Boto3_Error import capture_boto3_error
from osbot_aws.aws.boto3.View_Boto3_Rest_Calls import print_boto3_calls
from osbot_utils.testing.Duration import Duration
from osbot_utils.utils.Dev import pprint
from tests.integration.aws.bedrock.TestCase__Bedrock import TestCase__Bedrock


class test_Amazon_Titan_Text_Express_V1(TestCase__Bedrock):

    def setUp(self):
        self.model = Amazon_Titan_Text_Express_V1()

    def test___init__(self):
        expected_vars ={'input_text'      : ''                            ,
                        'max_token_count' : 1024                          ,
                        'model_id'        : 'amazon.titan-text-express-v1',
                        'stop_sequences' : []                             ,
                        'temperature'    : 0.0                            ,
                        'topP'           : 1                             }
        assert self.model.__locals__() == expected_vars


    #@print_boto3_calls()
    #@capture_boto3_error
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

    # def test_model_query(self):
    #     model_id ='amazon.titan-embed-image-v1:0'
    #     models = self.bedrock.models__by_id()
    #     model = models.get(model_id)
    #     pprint(model)
    #     return
    #     active_models = self.bedrock.models_active()
    #     model = active_models.get('ON_DEMAND').get('Amazon').get('TEXT').get(model_id)
    #     pprint(model)

    # see https://www.linkedin.com/feed/update/urn:li:activity:7167345154469658624/ for more details
    def test_bug_in_model_mapping(self):
        model_id = 'amazon.titan-embed-image-v1:0'
        inference_types_supported  = ['ON_DEMAND', 'PROVISIONED'    ] # BUG according to https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html
                                                                      # since this should only be an PROVISIONED model
        expected_model_data = { 'customizationsSupported': ['FINE_TUNING'                 ],
                                'inferenceTypesSupported': inference_types_supported       ,
                                'inputModalities'        : ['TEXT', 'IMAGE'               ],
                                'modelArn'               : 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-image-v1:0',
                                'modelId'                : model_id                        ,
                                'modelLifecycle'         : {'status': 'ACTIVE'            },
                                'modelName'              : 'Titan Multimodal Embeddings G1',
                                'outputModalities'       : ['EMBEDDING'                   ],
                                'providerName'           : 'Amazon'                         }
        models     = self.bedrock.models__by_id()
        model_data = models.get(model_id)
        assert model_data == expected_model_data