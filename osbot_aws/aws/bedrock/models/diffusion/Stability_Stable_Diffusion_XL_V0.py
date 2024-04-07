from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.utils.Png import save_png_base64_to_file


class Stability_Stable_Diffusion_XL_V0(Kwargs_To_Self):
    model_id          : str      = 'stability.stable-diffusion-xl-v0'
    text_prompts      : list
    cfg_scale         : int      = 10           # min: 0     max: 30     default: 10
    steps             : int      = 50           # min: 10    max: 150    default: 30
    seed              : int      = 42





    def body(self):
        return dict(text_prompts = self.text_prompts ,
                    cfg_scale    = self.cfg_scale    ,
                    steps        = self.steps        ,
                    seed         = self.seed         )

    def set_text_prompts(self, prompts):
        if prompts is not list:
            prompts = [prompts]
        text_prompts = []
        for prompt in prompts:
            text_prompts.append( {"text": prompt})
        self.text_prompts = text_prompts

    def save_png_data(self, png_data, target_file=None):
        if target_file is None:
            target_file = "/tmp/bedrock_image.png"
        save_png_base64_to_file(png_data, target_file)
