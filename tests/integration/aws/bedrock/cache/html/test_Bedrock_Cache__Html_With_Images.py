from unittest import TestCase

from osbot_aws.aws.bedrock.cache.html.Bedrock_Cache__Html_With_Images import Bedrock_Cache__Html_With_Images
from osbot_utils.utils.Files import file_exists, file_delete
from osbot_utils.utils.Json import json_dumps


class test_Bedrock_Cache__Html_With_Images(TestCase):

    def setUp(self):
        self.html_with_images = Bedrock_Cache__Html_With_Images()

    def test_create__amazon_titan(self):
        file_delete(self.html_with_images.target_file)
        self.html_with_images.create__amazon_titan()
        assert file_exists(self.html_with_images.target_file)

    def test_create__stable_diffusion(self):
        file_delete(self.html_with_images.target_file)
        self.html_with_images.create__stable_diffusion()
        assert file_exists(self.html_with_images.target_file)


