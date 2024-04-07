from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.utils.Png import save_png_base64_to_file


class Stability_Stable_Diffusion(Kwargs_To_Self):
    model_id          : str
    text_prompts      : list
    cfg_scale         : int      = 10
    steps             : int      = 50
    seed              : int      = 42

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