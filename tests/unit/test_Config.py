from unittest import TestCase

from osbot_aws.Config import Config


class test_Config(TestCase):

    def setUp(self) -> None:
        self.config = Config()

    def test__init__(self):
        print('here')

