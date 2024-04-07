from osbot_aws.aws.bedrock.models.diffusion.Stability_Stable_Diffusion import Stability_Stable_Diffusion
from osbot_aws.aws.bedrock.models.diffusion.Stability_Stable_Diffusion_XL_V1 import Stability_Stable_Diffusion_XL_V1
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.utils.Png import save_png_base64_to_file


class Stability_Stable_Diffusion_XL_V1__Text_To_Image(Stability_Stable_Diffusion_XL_V1):
    height  : int      = 512
    width   : int      = 512

    def body(self):
        return dict(**super().body()                                   ,
                    height                  = self.height              ,
                    width                   = self.width               )


