import pytest

from osbot_aws.aws.bedrock.models.diffusion.Stability_Stable_Diffusion_XL_V0 import Stability_Stable_Diffusion_XL_V0
from osbot_aws.aws.bedrock.models.mistral.Mistral_AI_7b_Instruct_v0_2 import Mistral_AI_7b_Instruct_v0_2
from osbot_aws.aws.boto3.Capture_Boto3_Error import capture_boto3_error
from osbot_aws.testing.TestCase__Bedrock import TestCase__Bedrock
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set, in_github_action


class test_Stability_Stable_Diffusion_XL_V0(TestCase__Bedrock):

    def setUp(self) -> None:
        if in_github_action():                                  # disabling Bedrock tests in GitHub actions since they are not 100% deterministic
            pytest.skip()
        self.model = Stability_Stable_Diffusion_XL_V0()
        self.png_data = None

    def tearDown(self):
        if self.png_data:
            target_file = '/tmp/stable_diffusion_image.png'
            self.model.save_png_data(png_data=self.png_data, target_file=target_file)

    def test__init__(self):
        expected_vars = { 'cfg_scale'      : 10                                  ,
                          'model_id'       : 'stability.stable-diffusion-xl-v0'  ,
                          'text_prompts'   : []                                  ,
                          'seed'           : 42                                  ,
                          'steps'          : 50                                  }
        assert self.model.__locals__() == expected_vars

    @capture_boto3_error
    def test_model_invoke(self):
        #self.cache.disable()
        #self.cache.update()
        prompts           = ['hello'                     ,                  # generates misc pics
                             'dog wearing black glasses' ,
                             'Renaissance-style portrait of an astronaut in space, detailed starry background, reflective helmet.',
                             'Abstract painting representing the sound of jazz music, using vibrant colors and erratic shapes'
                             ]
        current_prompt    = 3
        prompt            = prompts[current_prompt]

        self.model.set_text_prompts(prompt)
        model_id  = self.model.model_id
        body      = self.model.body()

        response  = self.bedrock.model_invoke(model_id, body)

        #pprint(response)
        artifacts = response.get('artifacts')
        assert list_set(response) == ['artifacts', 'result']
        assert len(artifacts) == 1
        self.png_data = artifacts[0].get('base64')
        #pprint(f'got image with size {len(self.png_data)}')