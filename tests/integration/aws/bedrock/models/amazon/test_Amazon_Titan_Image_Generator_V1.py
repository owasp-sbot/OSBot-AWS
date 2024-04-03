import pytest

from osbot_aws.aws.bedrock.models.amazon.Amazon_Titan_Image_Generator_V1 import Amazon_Titan_Image_Generator_V1
from osbot_aws.aws.boto3.Capture_Boto3_Error import capture_boto3_error
from osbot_utils.helpers.html.Tag__Base import Tag__Base
from osbot_utils.helpers.html.Tag__Div import Tag__Div
from osbot_utils.helpers.html.Tag__H import Tag__H
from osbot_utils.helpers.html.Tag__HR import Tag__HR
from osbot_utils.helpers.html.Tag__Head import Tag__Head
from osbot_utils.helpers.html.Tag__Html import Tag__Html
from osbot_utils.helpers.html.Tag__Link import Tag__Link
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import file_create
from osbot_utils.utils.Json import json_load
from osbot_utils.utils.Misc import list_set, in_github_action
from osbot_aws.testing.TestCase__Bedrock import TestCase__Bedrock
from osbot_utils.utils.Png import save_png_base64_to_file


#@pytest.mark.skip('skipping bedrock test for: Amazon_Titan_Image_Generator_V1')
class test_Amazon_Titan_Image_Generator_V1(TestCase__Bedrock):

    def setUp(self):
        if in_github_action():                                  # disabling Bedrock tests in GitHub actions since they are not 100% deterministic
            pytest.skip()
        self.model    = Amazon_Titan_Image_Generator_V1()
        self.png_data = None

    def tearDown(self):
        if self.png_data:
            target_file = '/tmp/titan_image.png'
            self.model.save_png_data(png_data=self.png_data, target_file=target_file)


    def test_model_invoke__TEXT_IMAGE(self):
        test_prompts =  [{"prompt"       : "A photograph of a cup of coffee from the side, with a dog drinking that coffee",
                          "negative_text": "" ,
                          "comment"      : "shows picture of dog drinking that coffee with the cup of coffee on top of a table"},
                         {"prompt"       : "A photograph of a cup of coffee from the side, with a dog drinking that coffee",
                          "negative_text": "table" ,
                          "comment"      : "negative text had no effect, table is still there"},
                         {"prompt"       : "A photograph of a cup of coffee from the side, with a dog drinking that coffee",
                          "negative_text": "black dogs" ,
                          "comment"      : "this worked, now we got a brown dog"},
                         {"prompt"       : "A photograph of a cup of coffee from the side, with a dog drinking that coffee",
                          "negative_text": "black or brown dogs" ,
                          "comment"      : "this didn't work very well, since now we got what it looks like a black dog"},
                         {"prompt"       : "a big X",
                          "negative_text": "" ,
                          "comment"      : "Here we get a big X"},
                         {"prompt"       : "a big X",
                          "negative_text": "blue" ,
                          "comment"      : "This didn't work since I was trying to remove the blue background"}]

        prompt_to_use = 5
        self.model.text          = test_prompts[prompt_to_use].get('prompt')         # set the prompt text
        self.model.negative_text = test_prompts[prompt_to_use].get('negative_text')  # set the negative text
        model_id                 = self.model.model_id                               # get the model_id (in this case 'amazon.titan-image-generator-v1')
        body                     = self.model.body()                                 # get the json data for this model

        text_to_image_params = {"text": self.model.text}                             # replicate the validation login
        if self.model.negative_text and len(self.model.negative_text) > 3:           # or it will fail AWS validation
            text_to_image_params["negativeText"] = self.model.negative_text

        assert model_id == 'amazon.titan-image-generator-v1'
        assert body     == {'imageGenerationConfig': { 'cfgScale'      : 10.0         ,
                                                       'height'        : 512          ,
                                                       'numberOfImages': 1            ,
                                                       'seed'          : 42           ,
                                                       'width'         : 512          },
                             'taskType'            :  'TEXT_IMAGE'                    ,
                             'textToImageParams'   : text_to_image_params             }

        response        = self.bedrock.model_invoke(model_id, body)         # invoke model using OSBot_AWS Bedrock api

        assert list_set(response) == ['error', 'images']
        error       = response.get('error')
        images      = response.get('images')
        self.png_data    = images.pop()
        assert error is None
        assert len(self.png_data) > 30000        # was first 513424 then 520564

    def test__see_images_in_cache(self):
        div_test_image = Tag__Div()
        div_images = []

        for request_data in self.cache.requests_data__with_model_id(self.model.model_id):
            request_hash        = request_data.get('_hash')
            request_id          = request_data.get('_id')
            model               = request_data.get('model')

            image_params        = request_data.get('body').get('textToImageParams')
            image_text          = image_params.get('text')
            image_negative_text = image_params.get('negativeText', "")
            response_data       = self.cache.response_data_for__request_hash(request_hash)
            images              = response_data.get('images')
            image_base64        = images[0]

            div_image = Tag__Div(tag_classes = ['col', 'col-md-3', 'text-center'])
            div_badge          = Tag__Div(tag_classes=['badge','bg-primary'], inner_html ="Cache item #0")
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
        css_style = """
                    .base64-image { width: 200px; 
                                    height: auto;
                                    margin-bottom: 1rem; }
                    .col          { border: 2px solid #C0C0FF;
                                    padding:10px }
                    .bg-dark { font-size:15px }
                    .var_name { font-size:12px }"""

        #link_bootstrap = Tag__Link(href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css", rel="stylesheet")
        head_style     = Tag__Base(tag_name='style', inner_html = css_style)
        head_tag       = Tag__Head(elements= [head_style])
        head_tag.title = text_title
        head_tag.add_css_bootstrap()
        html_tag       = Tag__Html(head=head_tag)
        html_tag.body.append(div_container )

        html_tag.save('/tmp/tmp-bedrock-images.html')