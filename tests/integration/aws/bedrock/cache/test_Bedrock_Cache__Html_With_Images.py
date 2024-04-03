from unittest import TestCase

from osbot_aws.aws.bedrock.cache.Bedrock_Cache__Html_With_Images import Bedrock_Cache__Html_With_Images
from osbot_aws.aws.bedrock.cache.Bedrock__Cache import Bedrock__Cache
from osbot_utils.helpers.html.Tag__Div import Tag__Div
from osbot_utils.utils.Files import file_exists


class test_Bedrock_Cache__Html_With_Images(TestCase):

    def setUp(self):
        self.html_with_images = Bedrock_Cache__Html_With_Images()

    def test_create(self):
        model_id = 'amazon.titan-image-generator-v1'
        self.html_with_images.create(model_id = model_id)
        assert file_exists(self.html_with_images.target_file)


