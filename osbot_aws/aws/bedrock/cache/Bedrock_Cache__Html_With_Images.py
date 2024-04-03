from osbot_aws.aws.bedrock.cache.Bedrock__Cache import Bedrock__Cache
from osbot_utils.helpers.html.Tag__Base import Tag__Base
from osbot_utils.helpers.html.Tag__Div import Tag__Div
from osbot_utils.helpers.html.Tag__H import Tag__H
from osbot_utils.helpers.html.Tag__HR import Tag__HR
from osbot_utils.helpers.html.Tag__Head import Tag__Head
from osbot_utils.helpers.html.Tag__Html import Tag__Html


class Bedrock_Cache__Html_With_Images:

    def __init__(self):
        self.cache       = Bedrock__Cache()
        self.target_file = '/tmp/tmp-bedrock-images.html'

    def create(self, model_id):
        div_test_image = Tag__Div()
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

        self.create_temp_html_file_with_images(div_images)


    def create_temp_html_file_with_images(self, div_images):
        text_title    = 'AWS Bedrock Cached images'
        div_container = Tag__Div(tag_classes=['container-fluid','my-5'])
        h_title       = Tag__H(1, text_title)
        hr            = Tag__HR()
        div_subtitle  = Tag__Div(tag_classes=['badge', 'bg-dark'], inner_html='for amazon.titan-image-generator-v1')
        div_row       = Tag__Div(tag_classes=['row'], elements=div_images)
        div_container.append(h_title,
                             div_subtitle,
                             hr,
                             div_row)

        css_data             = { ".base64-image" : { "width"         : "200px"           ,
                                                     "height"        : "auto"            ,
                                                     "margin-bottom" : "1rem"            },
                                 ".col"          : { "border"        : "2px solid #C0C0FF",
                                                     "padding"       : "10px"            },
                                 ".bg-dark"      : { "font-size"     : "15px"            },
                                 ".var_name"     : {"font-size"      : "12px"            }}


        head_style     = Tag__Base(tag_name='style')
        head_tag       = Tag__Head(elements= [head_style])
        head_tag.title = text_title
        head_tag.add_css_bootstrap()
        head_tag.style.set_css(css_data)
        html_tag       = Tag__Html(head=head_tag)
        html_tag.body.append(div_container )

        html_tag.save(self.target_file)