from unittest import TestCase

from osbot_aws.aws.lambda_.Dependencies import Dependencies


class test_Dependencies(TestCase):

    def setUp(self) -> None:
        dependencies = Dependencies()

