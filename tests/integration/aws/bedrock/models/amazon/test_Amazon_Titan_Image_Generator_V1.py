import pytest

from osbot_aws.aws.bedrock.models.amazon.Amazon_Titan_Image_Generator_V1 import Amazon_Titan_Image_Generator_V1
from osbot_aws.aws.boto3.Capture_Boto3_Error import capture_boto3_error
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set
from osbot_aws.testing.TestCase__Bedrock import TestCase__Bedrock
from osbot_utils.utils.Png import save_png_base64_to_file


@pytest.mark.skip('skipping bedrock test for: Amazon_Titan_Image_Generator_V1')
class test_Amazon_Titan_Image_Generator_V1(TestCase__Bedrock):

    def setUp(self):
        self.model = Amazon_Titan_Image_Generator_V1()

    #@cache_bedrock_respose
    def test_model_invoke(self):
        #prompt = "A photograph of a cup of coffee from the side, with a dog drinking that coffee"
        prompt = "a big X"
        self.model.text = prompt                                            # set the prompt text
        model_id        = self.model.model_id                               # get the model_id (in this case 'amazon.titan-image-generator-v1')
        body            = self.model.body()                                 # get the json data for this model

        assert model_id == 'amazon.titan-image-generator-v1'
        assert body     == {'imageGenerationConfig': { 'cfgScale'      : 10.0 ,
                                                       'height'        : 512  ,
                                                       'numberOfImages': 1    ,
                                                       'seed'          : 42   ,
                                                       'width'         : 512  },
                             'taskType'            :  'TEXT_IMAGE'             ,
                             'textToImageParams'   : { 'text'     : prompt     }}

        response        = self.bedrock.model_invoke(model_id, body)         # invoke model using OSBot_AWS Bedrock api

        assert list_set(response) == ['error', 'images']
        error       = response.get('error')
        images      = response.get('images')
        png_data    = images.pop()
        assert error is None
        assert len(png_data) == 513424
        target_file = '/tmp/titan_image.png'
        self.model.save_png_data(png_data=png_data, target_file=target_file)
        #pprint(error)