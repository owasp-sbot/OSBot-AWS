from unittest import TestCase

from osbot_aws.aws.bedrock.cache.html.Bedrock_Cache__Html_Table import Bedrock_Cache__Html_Table
from osbot_utils.utils.Files import file_delete, file_exists


class test_Bedrock_Cache__Html_Table(TestCase):

    def setUp(self):
        self.html_table = Bedrock_Cache__Html_Table()

    def test_create(self):
        file_delete(self.html_table.target_file)
        self.html_table.create()
        assert file_exists(self.html_table.target_file)