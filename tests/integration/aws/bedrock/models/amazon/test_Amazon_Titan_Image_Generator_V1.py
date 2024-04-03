import pytest

from osbot_aws.aws.bedrock.models.amazon.Amazon_Titan_Image_Generator_V1 import Amazon_Titan_Image_Generator_V1
from osbot_utils.utils.Misc import list_set, in_github_action
from osbot_aws.testing.TestCase__Bedrock import TestCase__Bedrock


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
        prompt_to_use = 5
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

