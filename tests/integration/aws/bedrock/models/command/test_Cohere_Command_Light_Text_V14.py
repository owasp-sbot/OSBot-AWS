from osbot_aws.aws.bedrock.models.command.Cohere_Command_Light_Text_V14 import Cohere_Command_Light_Text_V14
from osbot_aws.aws.bedrock.models.command.Cohere_Command_Text_V14 import Cohere_Command_Text_V14
from osbot_aws.aws.boto3.Capture_Boto3_Error import capture_boto3_error
from osbot_aws.testing.TestCase__Bedrock import TestCase__Bedrock
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set


class test_Cohere_Command_Light_Text_V14(TestCase__Bedrock):

    def setUp(self) -> None:
        self.model = Cohere_Command_Light_Text_V14()

    def test__init__(self):
        expected_vars = {   'k'                 : 0                              ,
                            'max_tokens'        : 1024                           ,
                            'model_id'          : 'cohere.command-light-text-v14',
                            'num_generations'   : 1                              ,
                            'p'                 : 1.0                            ,
                            'prompt'            : ''                             ,
                            'return_likelihoods': 'NONE'                         ,
                            'stop_sequences'    : []                             ,
                            'stream'            : False                          ,
                            'temperature'       : 0.0                            ,
                            'truncate'          : 'NONE'                         }
        assert self.model.__locals__() == expected_vars

    @capture_boto3_error
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

        assert list_set(response) == ['generations', 'id', 'prompt']