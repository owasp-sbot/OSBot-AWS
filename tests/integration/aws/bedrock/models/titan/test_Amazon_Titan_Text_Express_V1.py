import pytest

from osbot_aws.aws.bedrock.models.titan.Amazon_Titan_Text_Express_V1 import Amazon_Titan_Text_Express_V1
from osbot_aws.testing.TestCase__Bedrock import TestCase__Bedrock
from osbot_utils.utils.Misc import in_github_action

# todo: now that we have a cache, re-enable this test
@pytest.mark.skip('skipping bedrock test for: amazon.titan-text-express-v1')
class test_Amazon_Titan_Text_Express_V1(TestCase__Bedrock):

    def setUp(self):
        if in_github_action():                                  # disabling Bedrock tests in GitHub actions since they are not 100% deterministic
            pytest.skip()
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