from osbot_aws.aws.bedrock.cache.Bedrock__Cache import Bedrock__Cache
from osbot_aws.aws.bedrock.cache.html.Bedrock_Cache__Html import Bedrock_Cache__Html
from osbot_utils.helpers.html.Tag__Base import Tag__Base
from osbot_utils.helpers.html.Tag__Div import Tag__Div
from osbot_utils.helpers.html.Tag__H import Tag__H
from osbot_utils.helpers.html.Tag__HR import Tag__HR
from osbot_utils.helpers.html.Tag__Head import Tag__Head
from osbot_utils.helpers.html.Tag__Html import Tag__Html
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set


class Bedrock_Cache__Html_With_Images(Bedrock_Cache__Html):


    def __init__(self):
        super().__init__()
        self.title     = 'AWS Bedrock Cached images'
        self.target_file = '/tmp/tmp-bedrock-images.html'


    def create__amazon_titan(self):
        div_images = []
        model_id  = 'amazon.titan-image-generator-v1'
        self.sub_title = f'for {model_id}'
        for request_data in self.cache.requests_data__with_model_id(model_id):
            request_hash        = request_data.get('_hash'    )
            request_id          = request_data.get('_id'      )
            request_comments    = request_data.get('_comments')
            request_body        = request_data.get('body'     )
            task_type           = request_body.get('taskType' )
            if task_type == 'TEXT_IMAGE':
                image_params = request_body.get('textToImageParams', {})
            elif task_type == 'IMAGE_VARIATION':
                image_params = request_body.get('imageVariationParams', {})
            elif task_type == 'INPAINTING':
                image_params = request_body.get('inPaintingParams', {})
            elif task_type == 'OUTPAINTING':
                image_params = request_body.get('outPaintingParams', {})
            else:
                image_params = {}
            image_text          = image_params.get('text')
            image_negative_text = image_params.get('negativeText', "")
            response_data       = self.cache.response_data_for__request_hash(request_hash)
            images              = response_data.get('images')
            image_base64        = images[0]

            div_image = Tag__Div(tag_classes = ['col', 'col-md-3', 'text-center'])
            div_badge          = Tag__Div(tag_classes=['badge','bg-primary'], inner_html = f"{task_type} #{request_id}")
            hr                 = Tag__HR()
            div_text_title     = Tag__Div(tag_classes=['var_name'], inner_html="Text:"          )
            div_text_value     = Tag__Div(inner_html=f"<strong>{image_text}</strong>"           )
            div_negative_title = Tag__Div(tag_classes=['var_name'], inner_html="Negative Text:" )
            div_negative_value = Tag__Div(inner_html=f"<strong>{image_negative_text}</strong>"  )
            div_comments_title = Tag__Div(tag_classes=['var_name'      ], inner_html="Comments:"      )
            div_comments_value = Tag__Div(tag_classes=['comments_value'], inner_html=request_comments  )
            img                = Tag__Base(tag_name="img", tag_classes=['base64-image','img-fluid'])
            img.attributes['src'] = f"data:image/jpeg;base64,{image_base64}"
            div_image.append(div_badge, hr,
                             img,
                             div_text_title   , div_text_value     ,
                             div_negative_title, div_negative_value,
                             div_comments_title, div_comments_value)
            div_images.append(div_image)

        self.row_elements = div_images

        self.create_html_file()

    def create__stable_diffusion(self):

        div_images = []
        #model_id = 'stability.stable-diffusion-xl-v0'
        model_id = 'stability.stable-diffusion-xl-v1'
        self.sub_title = f'for {model_id}'

        for request_data in self.cache.requests_data__with_model_id(model_id):
            request_hash        = request_data.get('_hash'    )
            request_id          = request_data.get('_id'      )
            #request_comments    = request_data.get('_comments')
            request_body        = request_data.get('body'     )
            response_data       = self.cache.response_data_for__request_hash(request_hash)
            artifacts           = response_data.get('artifacts')
            artifact            = artifacts[0]
            image_base64        = artifact['base64']
            cfg_scale           = request_body.get('cfg_scale')
            steps               = request_body.get('steps')
            text_prompts        = request_body.get('text_prompts')
            text_prompt         = text_prompts[0].get('text')
            image_text          = '....'
            div_image = Tag__Div(tag_classes = ['col', 'col-md-3', 'text-center'])
            div_badge          = Tag__Div(tag_classes=['badge','bg-primary'], inner_html = f"quality {steps} prompt #{cfg_scale}")
            hr                 = Tag__HR()
            div_text_title     = Tag__Div(tag_classes=['var_name'], inner_html="Text:"          )
            div_text_value     = Tag__Div(inner_html=f"<strong>{text_prompt}</strong>"           )
            # div_negative_title = Tag__Div(tag_classes=['var_name'], inner_html="Negative Text:" )
            # div_negative_value = Tag__Div(inner_html=f"<strong>{image_negative_text}</strong>"  )
            # div_comments_title = Tag__Div(tag_classes=['var_name'      ], inner_html="Comments:"      )
            # div_comments_value = Tag__Div(tag_classes=['comments_value'], inner_html=request_comments  )
            img                = Tag__Base(tag_name="img", tag_classes=['base64-image','img-fluid'])
            img.attributes['src'] = f"data:image/jpeg;base64,{image_base64}"
            div_image.append(div_badge, hr,
                             img,
                             div_text_title   , div_text_value     )
                             # div_negative_title, div_negative_value,
                             # div_comments_title, div_comments_value)
            div_images.append(div_image)

            # print(cfg_scale, steps)
            # print(len(image_base64))
        self.row_elements = div_images
        self.create_html_file()

