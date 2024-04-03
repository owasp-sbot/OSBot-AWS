import pytest

from osbot_aws.aws.bedrock.models.amazon.Amazon_Titan_Image_Generator_V1 import Amazon_Titan_Image_Generator_V1
from osbot_aws.aws.boto3.Capture_Boto3_Error import capture_boto3_error
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

        prompt_to_use = 1
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

    #@pytest.mark.skip(reason="not implemented")
    def test__see_images_in_cache(self):

        images_html_code = ''
        for request_data in self.cache.requests_data__with_model_id(self.model.model_id):
            request_hash        = request_data.get('_hash')
            request_id          = request_data.get('_id')
            model               = request_data.get('model')

            image_params        = request_data.get('body').get('textToImageParams')
            image_text          = image_params.get('text')
            image_negative_text = image_params.get('negativeText', "")
            response_data = self.cache.response_data_for__request_hash(request_hash)
            images        = response_data.get('images')
            image_base64  = images[0]
            image_html_code = f"""<div class="col col-md-3 text-center">
                                    <div class="badge bg-primary">Cache item #{request_id}</div>
                                    <hr/>                                    
                                    <img class="base64-image img-fluid" src="data:image/jpeg;base64,{image_base64}">
                                    <div class="var_name">Text:</div>
                                    <div><strong>{image_text}</strong></div>
                                    <hr/>
                                    <div class="var_name">Negative Text</div> 
                                    <div><strong>{image_negative_text}</strong></div>
                                  </div>"""
            images_html_code += image_html_code

        # images_code = ""
        # for image_base64 in images_base64:
        #
        #     images_code += image_code
        html_code = """
<!DOCTYPE html>
<html>
<head>
    <title>AWS Bedrock Cached Images</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">    
     <style>
        .base64-image {
            width: 200px; /* Example width, adjust as needed */
            height: auto;
            margin-bottom: 1rem; /* Bootstrap spacing */
        }
        .col {
            border: 2px solid #C0C0FF;
            padding:10px
        }
        .bg-dark { font-size:15px }
        .var_name { font-size:12px }        
    </style>
</head>
<body>
    <div class="container-fluid my-5">    
        <h1>AWS Bedrock Cached images</h1>    
    <div class="badge bg-dark">
        for amazon.titan-image-generator-v1
    </div>
    <hr/>
    
    
        <div class="row">
            """ + images_html_code +  """
        </div>
    </div>
</div>
</body>
</html>
"""
        tmp_html_file = '/tmp/tmp-bedrock-images.html'
        file_create(tmp_html_file, html_code)