from osbot_aws.aws.bedrock.models.mistral.Mistral_AI_Large_2402_v1_0    import Mistral_AI_Large_2402_v1_0
from osbot_aws.aws.boto3.Capture_Boto3_Error                            import capture_boto3_error
from osbot_aws.testing.TestCase__Bedrock                                import TestCase__Bedrock
from osbot_utils.utils.Dev import pprint

from osbot_utils.utils.Misc import list_set

class test_Mistral_AI_Large_2402_v1_0(TestCase__Bedrock):

    def setUp(self) -> None:
        self.model = Mistral_AI_Large_2402_v1_0()

    def test__init__(self):
        expected_vars = { 'max_tokens'     : 1024                                  ,
                          'model_id'       : 'mistral.mistral-large-2402-v1:0'  ,
                          'prompt'         : ''                                    ,
                          'stop'           : []                                    ,
                          'temperature'    : 0.0                                   ,
                          'top_k'          : 1                                     ,
                          'top_p'          : 1.0                                   }
        assert self.model.__locals__() == expected_vars

    @capture_boto3_error
    def test_model_invoke(self):
        #self.cache.disable()

        prompts           = ['hello'                                                                ,       # without mistral prompt formatting
                             'what is your model?'                                                  ,       #    providing direct questions results in weird completion results
                             'what is 40 + 2'                                                       ,       #    NOTE: this one looked like a tweet or a SO comment
                             '<s>[INST] What is your favourite condiment? [/INST]'                  ,       # with this <s>[INST] format we get good answers
                             """<s>[INST] In Bash, how do I list all text files in                          
                                          the current directory (excluding subdirectories)      
                                          that have been modified in the last month? [/INST]"""     ,
                             '<s>[INST]Hello[/INST]',
                             '<s>[INST]what is your model?[/INST]',
                             '<s>[INST]what is 40 + 2[/INST]',
                             ]
        current_prompt    = 2
        prompt            = prompts[current_prompt]

        self.model.prompt = prompt
        model_id  = self.model.model_id
        body      = self.model.body()

        response  = self.bedrock.model_invoke(model_id, body)

        #pprint(response)

        assert list_set(response) == ['outputs']