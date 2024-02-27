import pytest

from osbot_aws.aws.bedrock.models.amazon.Amazon_Titan_Image_Generator_V1 import Amazon_Titan_Image_Generator_V1
from osbot_aws.aws.boto3.Capture_Boto3_Error import capture_boto3_error
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set
from osbot_utils.utils.Png import save_png_base64_to_file
from tests.integration.aws.bedrock.TestCase__Bedrock import TestCase__Bedrock

@pytest.mark.skip('skipping bedrock test for: Amazon_Titan_Image_Generator_V1')
class test_Amazon_Titan_Image_Generator_V1(TestCase__Bedrock):

    def setUp(self):
        self.model = Amazon_Titan_Image_Generator_V1()

    @capture_boto3_error
    def test_model_invoke(self):
        prompt = "A photograph of a cup of coffee from the side, with a dog drinking that coffee. The dog should have a big smile"
        prompt = "a big X"
        self.model.text = prompt
        model_id  = self.model.model_id
        body      = self.model.body()
        response  = self.bedrock.model_invoke(model_id, body)
        assert list_set(response) == ['error', 'images']
        error       = response.get('error')
        images      = response.get('images')
        png_data    = images.pop()
        target_file = '/tmp/titan_image.png'
        #pprint(save_png_base64_to_file(png_data, target_file))
        assert error is None
        assert len(png_data) == 513424
        #pprint(error)