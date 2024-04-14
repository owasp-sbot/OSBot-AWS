from osbot_aws.aws.bedrock.models.diffusion.Stability_Stable_Diffusion import Stability_Stable_Diffusion
from osbot_aws.aws.bedrock.models.diffusion.Stability_Stable_Diffusion_XL_V1 import Stability_Stable_Diffusion_XL_V1
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.utils.Png import save_png_base64_to_file


class Stability_Stable_Diffusion_XL_V1__Image_To_Image(Stability_Stable_Diffusion_XL_V1):
    init_image      : str                           # The base64 encoded image that you want to use to initialize the diffusion process.
    init_image_mode : str     = 'IMAGE_STRENGTH'    # (Optional) Determines whether to use image_strength or step_schedule_* to control how much influence the image in init_image has on the result. Possible values are IMAGE_STRENGTH or STEP_SCHEDULE.
    image_strength  : float   = 1.0                 # (Optional) Determines how much influence the source image in init_image has on the diffusion process. Values close to 1 yield images very similar to the source image. Values close to 0 yield images very different than the source image.

    def body(self):
        return dict(**super().body()                                   ,
                    init_image      = self.init_image      ,
                    init_image_mode = self.init_image_mode ,
                    strength        = self.image_strength  )


