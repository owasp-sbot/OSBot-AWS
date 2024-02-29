from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self


class Amazon_Titan_Image_Generator_V1(Kwargs_To_Self):
    model_id         : str = 'amazon.titan-image-generator-v1'
    text             : str
    #negative_text    : str
    number_of_images : int  = 1
    height           : int  = 512  #512
    width            : int  = 512  #512
    cfg_scale        : float = 10.0
    seed             : int   = 42           # just because

    def body(self):
        return {"taskType"             : "TEXT_IMAGE",
                "textToImageParams"    : { "text"          : self.text            ,
                                           #"negativeText"  : self.negative_text
                                           },
                "imageGenerationConfig": { "numberOfImages": self.number_of_images,
                                           "height"        : self.height          ,
                                           "width"         : self.width           ,
                                           "cfgScale"      : self.cfg_scale       ,
                                           "seed"          : self.seed            }}