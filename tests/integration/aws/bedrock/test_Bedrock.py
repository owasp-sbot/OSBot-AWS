from unittest import TestCase

import botocore
from botocore import client

from osbot_aws.aws.bedrock.Bedrock import Bedrock
from osbot_utils.utils.Objects import type_full_name


class test_Bedrock(TestCase):

    def setUp(self):
        self.bedrock = Bedrock()

    def test_client(self):
        assert type_full_name(self.bedrock.client()) == 'botocore.client.Bedrock'