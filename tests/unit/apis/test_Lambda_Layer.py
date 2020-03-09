import os
from unittest import TestCase
from datetime import datetime

import gw_bot
from gw_bot.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.Lambda_Layer import Lambda_Layer
from osbot_utils.utils.Files import Files


class test_Lambda_Layer(Test_Helper):

    def setUp(self):
        super().setUp()
        self.source_path      = os.path.dirname(gw_bot.__file__)[0:-8] + "../modules/sdk-eval-toolset/libraries/linux"        # todo: move to dedicated class
        self.folders_mapping  = { self.source_path: 'lib/sdk-eval-toolset'}
        self.api              = Lambda_Layer(name="glasswall_editor_engine", folders_mapping = self.folders_mapping, s3_bucket=f'gw-bot-test-layer-bucket-{datetime.now().timestamp()}')

    def test_setUp(self):
        Files.exists(self.source_path)

    def test_create_lambda_layer(self):
        self.assertEqual(type(self.api.create()), str)
        self.assertEqual(self.api.delete(with_s3_bucket=True), True)

