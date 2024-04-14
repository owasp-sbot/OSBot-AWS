from osbot_aws.aws.bedrock.models.diffusion.Stability_Stable_Diffusion import Stability_Stable_Diffusion
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.utils.Misc import list_set
from osbot_utils.utils.Png import save_png_base64_to_file


class Stability_Stable_Diffusion_XL_V1(Stability_Stable_Diffusion):
    model_id            : str      = 'stability.stable-diffusion-xl-v1'
    samples             : int      = 1
    #clip_guidance_preset: str      = 'NONE'         # FAST_BLUE, FAST_GREEN, NONE, SIMPLE SLOW, SLOWER, SLOWEST.
    #sampler             : str                       # DDIM, DDPM, K_DPMPP_2M, K_DPMPP_2S_ANCESTRAL, K_DPM_2, K_DPM_2_ANCESTRAL, K_EULER, K_EULER_ANCESTRAL, K_HEUN K_LMS.
    #style_preset        : str                       # 3d-model, analog-film, anime, cinematic, comic-book, digital-art, enhance, fantasy-art, isometric, line-art, low-poly, modeling-compound, neon-punk, origami, photographic, pixel-art, tile-texture
    #extras              : dict

    def body(self):
        return dict(text_prompts            = self.text_prompts        ,
                    cfg_scale               = self.cfg_scale           ,
                    steps                   = self.steps               ,
                    seed                    = self.seed                ,
                    samples                 = self.samples             ,
                    #clip_guidance_preset    = self.clip_guidance_preset,
                    # sampler               = self.# sampler           ,
                    #style_preset            = self.style_preset        ,
                    #extras                  = self.extras
                    )

    def invoke(self, bedrock, prompts):
        self.set_text_prompts(prompts)
        response  = bedrock.model_invoke(self.model_id, self.body())
        if response:
            artifacts = response.get('artifacts')
            if list_set(response) == ['artifacts', 'result']:
                if len(artifacts) == 1:
                    artifact = artifacts[0]
                    return artifact.get('base64')

    def comments(self, cache):
        model_id = self.model_id
        body = self.body()
        return cache.cache_entry_comments(model_id=model_id, body=body)


