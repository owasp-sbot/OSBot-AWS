from unittest import TestCase

from osbot_utils.utils.Dev import pprint

from osbot_aws.helpers.Lambda_Layers_OSBot import Lambda_Layers_OSBot


class test_Lambda_Layers_OSBot(TestCase):

    def setUp(self):
        self.lambda_layers_osbot = Lambda_Layers_OSBot()

    def test_osbot_utils(self):
        layer_arn = self.lambda_layers_osbot.osbot_utils()
        assert 'layer_for__osbot_utils' in layer_arn

    def test_osbot_aws(self):
        layer_arn = self.lambda_layers_osbot.osbot_aws()
        assert 'layer_for__osbot_aws' in layer_arn
