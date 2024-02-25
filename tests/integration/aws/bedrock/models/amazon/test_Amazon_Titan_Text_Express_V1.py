from unittest import TestCase

from osbot_aws.aws.bedrock.models.amazon.Amazon_Titan_Text_Express_V1 import Amazon_Titan_Text_Express_V1


class test_Amazon_Titan_Text_Express_V1(TestCase):

    def setUp(self):
        self.model = Amazon_Titan_Text_Express_V1()

    def test___init__(self):
        expected_vars = {}
        assert self.model.__locals__() == expected_vars