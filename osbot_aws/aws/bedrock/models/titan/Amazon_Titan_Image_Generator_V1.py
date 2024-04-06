from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Png import save_png_base64_to_file

# see https://docs.aws.amazon.com/bedrock/latest/userguide/titan-image-models.html
#     https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-titan-image.html
class Amazon_Titan_Image_Generator_V1(Kwargs_To_Self):
    model_id         : str = 'amazon.titan-image-generator-v1'
    text             : str
    negative_text    : str
    number_of_images : int  = 1
    height           : int  = 512  #512
    width            : int  = 512  #512
    cfg_scale        : float = 10.0
    seed             : int   = 42           # just because

    # IMAGE_VARIATION
    def body__image_variation(self, images):
        image_variation_params = dict(**self.text_and_negative_text(),
                                      images=images)
        return {"taskType"             : "IMAGE_VARIATION"              ,
                "imageVariationParams" : image_variation_params         ,
                "imageGenerationConfig": self.image_generation_config() }

    # INPAINTING
    def body__in_painting(self, image, mask_prompt):
        in_painting_params = dict(**self.text_and_negative_text(),
                                  image      = image             ,
                                  maskPrompt = mask_prompt       )
        return {"taskType"             : "INPAINTING",
                "inPaintingParams"     : in_painting_params,
                "imageGenerationConfig": self.image_generation_config()}

    # INPAINTING
    def body__out_painting(self, image, mask_prompt):
        out_painting_params = dict(**self.text_and_negative_text(),
                                  image           = image             ,
                                  maskPrompt      = mask_prompt       ,
                                  outPaintingMode = "DEFAULT"         )
        return {"taskType"             : "OUTPAINTING",
                "outPaintingParams"    : out_painting_params,
                "imageGenerationConfig": self.image_generation_config()}

    #TEXT_IMAGE

    def body__text_image(self):
        text_to_image_params = { "text": self.text }
        if self.negative_text and len(self.negative_text) > 3:                  # or it will fail AWS validation
            text_to_image_params["negativeText"] = self.negative_text
        return {"taskType"             : "TEXT_IMAGE"                             ,
                "textToImageParams"    : text_to_image_params                     ,
                "imageGenerationConfig": { "numberOfImages": self.number_of_images,
                                           "height"        : self.height          ,
                                           "width"         : self.width           ,
                                           "cfgScale"      : self.cfg_scale       ,
                                           "seed"          : self.seed            }}



    def image_generation_config(self):
        return { "numberOfImages": self.number_of_images,
                 "height"        : self.height          ,
                 "width"         : self.width           ,
                 "cfgScale"      : self.cfg_scale       }

    def text_and_negative_text(self):
        result = {"text": self.text}
        if self.negative_text and len(self.negative_text) > 3:  # or it will fail AWS validation
            result["negativeText"] = self.negative_text
        return result

    def save_png_data(self, png_data, target_file=None):
        if target_file is None:
            target_file = "/tmp/bedrock_image.png"
        save_png_base64_to_file(png_data, target_file)