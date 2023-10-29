from unittest import TestCase

from osbot_utils.utils.Dev import pprint

from osbot_aws.helpers.Lambda_Layers_OSBot import Lambda_Layers_OSBot


class test_Lambda_Layers_OSBot(TestCase):

    def setUp(self):
        self.lambda_layers_osbot = Lambda_Layers_OSBot()

    def test_create__fastapi(self):
        layer_arn = self.lambda_layers_osbot.create__fastapi()
        assert 'layer_for__fastapi' in layer_arn
        pprint(layer_arn)

    def test_create__flask(self):
        layer_arn = self.lambda_layers_osbot.create__flask()
        assert 'layer_for__flask' in layer_arn
        pprint(layer_arn)

    def test_create__llms(self):
        layer_arn = self.lambda_layers_osbot.create__llms()
        assert 'layer_for__llms' in layer_arn
        pprint(layer_arn)

    def test_create__osbot_aws(self):
        layer_arn = self.lambda_layers_osbot.create__osbot_aws()
        assert 'layer_for__osbot_aws' in layer_arn
        pprint(layer_arn)

    def test_create__osbot_utils(self):
        layer_arn = self.lambda_layers_osbot.create__osbot_utils()
        assert 'layer_for__osbot_utils' in layer_arn
        pprint(layer_arn)

    def test_osbot_utils(self):
        layer_arn = self.lambda_layers_osbot.osbot_utils()
        assert 'layer_for__osbot_utils' in layer_arn

    def test_osbot_aws(self):
        layer_arn = self.lambda_layers_osbot.osbot_aws()
        assert 'layer_for__osbot_aws' in layer_arn
        pprint(layer_arn)
