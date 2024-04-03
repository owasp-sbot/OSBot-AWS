from osbot_aws.aws.bedrock.cache.Bedrock__Cache import Bedrock__Cache
from osbot_aws.aws.bedrock.cache.html.Bedrock_Cache__Html import Bedrock_Cache__Html
from osbot_utils.helpers.html.Tag__Base import Tag__Base
from osbot_utils.helpers.html.Tag__Div import Tag__Div
from osbot_utils.helpers.html.Tag__H import Tag__H
from osbot_utils.helpers.html.Tag__HR import Tag__HR
from osbot_utils.helpers.html.Tag__Head import Tag__Head
from osbot_utils.helpers.html.Tag__Html import Tag__Html


class Bedrock_Cache__Html_With_Images(Bedrock_Cache__Html):


    def __init__(self):
        super().__init__()
        self.title     = 'AWS Bedrock Cached images'
        self.sub_title = 'for amazon.titan-image-generator-v1'

    def create(self, model_id):
        div_images = []

        for request_data in self.cache.requests_data__with_model_id(model_id):
            request_hash        = request_data.get('_hash')
            request_id          = request_data.get('_id')
            #model               = request_data.get('model')

            image_params        = request_data.get('body').get('textToImageParams')
            image_text          = image_params.get('text')
            image_negative_text = image_params.get('negativeText', "")
            response_data       = self.cache.response_data_for__request_hash(request_hash)
            images              = response_data.get('images')
            image_base64        = images[0]

            div_image = Tag__Div(tag_classes = ['col', 'col-md-3', 'text-center'])
            div_badge          = Tag__Div(tag_classes=['badge','bg-primary'], inner_html = f"Cache item #{request_id}")
            hr                 = Tag__HR()
            div_text_title     = Tag__Div(tag_classes=['var_name'], inner_html="Text:")
            div_text_value     = Tag__Div(inner_html=f"<strong>{image_text}</strong>")
            div_negative_title = Tag__Div(tag_classes=['var_name'], inner_html="Negative Text:")
            div_negative_value = Tag__Div(inner_html=f"<strong>{image_negative_text}</strong>")

            img                = Tag__Base(tag_name="img", tag_classes=['base64-image','img-fluid'])
            img.attributes['src'] = f"data:image/jpeg;base64,{image_base64}"
            div_image.append(div_badge, hr, img, div_text_title, div_text_value, div_negative_title, div_negative_value)
            div_images.append(div_image)

        self.row_elements = div_images

        self.create_html_file()


