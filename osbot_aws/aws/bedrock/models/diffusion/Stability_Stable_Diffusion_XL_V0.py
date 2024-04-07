from osbot_aws.aws.bedrock.models.diffusion.Stability_Stable_Diffusion import Stability_Stable_Diffusion
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.utils.Png import save_png_base64_to_file


class Stability_Stable_Diffusion_XL_V0(Stability_Stable_Diffusion):
    model_id: str = 'stability.stable-diffusion-xl-v0'

    def body(self):
        return dict(text_prompts = self.text_prompts ,
                    cfg_scale    = self.cfg_scale    ,   # min: 0     max: 30     default: 10
                    steps        = self.steps        ,   # min: 10    max: 150    default: 30
                    seed         = self.seed         )


