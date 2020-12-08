import os
from unittest import TestCase

from osbot_aws.Config import Config


class test_Config(TestCase):

    def setUp(self) -> None:
        self.config = Config()

    def test__init__(self):
        assert type(os.environ['aws_access_key_id'    ]) is str
        assert type(os.environ['aws_secret_access_key']) is str
        assert type(os.environ['aws_session_token'    ]) is str

