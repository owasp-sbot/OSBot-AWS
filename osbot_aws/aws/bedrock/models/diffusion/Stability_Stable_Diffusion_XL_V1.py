from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.utils.Png import save_png_base64_to_file


class Stability_Stable_Diffusion_XL_V1(Kwargs_To_Self):
    model_id            : str      = 'stability.stable-diffusion-xl-v1'
    text_prompts        : list
    cfg_scale           : int      = 7              # min: 0     max: 35    default: 7
    steps               : int      = 50             # min: 10    max: 50    default: 30
    seed                : int      = 42
    height              : int      = 512
    width               : int      = 512
    clip_guidance_preset: str      = 'NONE'         # FAST_BLUE, FAST_GREEN, NONE, SIMPLE SLOW, SLOWER, SLOWEST.
    #sampler             : str                      # DDIM, DDPM, K_DPMPP_2M, K_DPMPP_2S_ANCESTRAL, K_DPM_2, K_DPM_2_ANCESTRAL, K_EULER, K_EULER_ANCESTRAL, K_HEUN K_LMS.
    samples             : int      = 1
    style_preset        : str                       # 3d-model, analog-film, anime, cinematic, comic-book, digital-art, enhance, fantasy-art, isometric, line-art, low-poly, modeling-compound, neon-punk, origami, photographic, pixel-art, tile-texture
    extras              : dict



    def body(self):
        return dict(text_prompts            = self.text_prompts        ,
                    cfg_scale               = self.cfg_scale           ,
                    steps                   = self.steps               ,
                    seed                    = self.seed                ,
                    height                  = self.height              ,
                    width                   = self.width               ,
                    #clip_guidance_preset    = self.clip_guidance_preset,
                    # sampler               = self.# sampler           ,
                    samples                 = self.samples             ,
                    #style_preset            = self.style_preset        ,
                    #extras                  = self.extras
                    )

    def set_text_prompts(self, prompts, weight=0):
        if prompts is not list:
            prompts = [prompts]
        text_prompts = []
        for prompt in prompts:
            text_prompts.append( {  "text": prompt,
                                    #'weight': weight}
                                  })
        self.text_prompts = text_prompts

    def save_png_data(self, png_data, target_file=None):
        if target_file is None:
            target_file = "/tmp/bedrock_image.png"
        save_png_base64_to_file(png_data, target_file)
