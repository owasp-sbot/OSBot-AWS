import pytest

from osbot_aws.aws.bedrock.models.diffusion.Stability_Stable_Diffusion_XL_V0 import Stability_Stable_Diffusion_XL_V0
from osbot_aws.aws.bedrock.models.diffusion.Stability_Stable_Diffusion_XL_V1 import Stability_Stable_Diffusion_XL_V1
from osbot_aws.aws.bedrock.models.diffusion.Stability_Stable_Diffusion_XL_V1__Image_To_Image import \
    Stability_Stable_Diffusion_XL_V1__Image_To_Image
from osbot_aws.aws.bedrock.models.diffusion.Stability_Stable_Diffusion_XL_V1__Text_To_Image import \
    Stability_Stable_Diffusion_XL_V1__Text_To_Image
from osbot_aws.aws.bedrock.models.mistral.Mistral_AI_7b_Instruct_v0_2 import Mistral_AI_7b_Instruct_v0_2
from osbot_aws.aws.boto3.Capture_Boto3_Error import capture_boto3_error
from osbot_aws.testing.TestCase__Bedrock import TestCase__Bedrock
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set, in_github_action


class test_Stability_Stable_Diffusion_XL_V1__Image_To_Image(TestCase__Bedrock):

    def setUp(self) -> None:
        if in_github_action():                                  # disabling Bedrock tests in GitHub actions since they are not 100% deterministic
            pytest.skip()
        self.model = Stability_Stable_Diffusion_XL_V1__Image_To_Image()
        self.png_data = None

    def tearDown(self):
        if self.png_data:
            target_file = '/tmp/stable_diffusion_image.png'
            self.model.save_png_data(png_data=self.png_data, target_file=target_file)

    def test__init__(self):
        expected_vars = {   'cfg_scale'      : 10                                   ,
                            'model_id'       : 'stability.stable-diffusion-xl-v1'   ,
                            'samples'        : 1                                    ,
                            'seed'           : 42                                   ,
                            'steps'          : 50                                   ,
                            'text_prompts'   : []                                   ,
                            'init_image'     : ''                                   ,
                            'init_image_mode': 'IMAGE_STRENGTH'                     ,
                            'image_strength' : 1.0                                  }
        assert self.model.__locals__() == expected_vars

    def get_init_image_from_cache(self, prompt):
        self.cache.only_from_cache()
        model    = Stability_Stable_Diffusion_XL_V1__Text_To_Image()
        png_data = model.invoke(self.bedrock, prompt)
        self.cache.only_from_cache(False)
        return png_data


    @capture_boto3_error
    def test_model_invoke(self):
        #self.cache.update()
        init_image_prompt = 'dog wearing black glasses'
        prompts           = ["tiger with glasses"]
        current_prompt    = 0
        prompt            = prompts[current_prompt]

        init_image = self.get_init_image_from_cache(init_image_prompt)
        assert init_image and len(init_image) > 10000

        #self.cache.disable()
        #pprint(self.model.body())
        self.model.init_image = init_image

        self.png_data         = self.model.invoke(self.bedrock, prompt)
        #self.cache.comments_set(self.model, "didn't work very well, the tiger wasn't well captured")
        #self.cache.comments_print(self.model)

