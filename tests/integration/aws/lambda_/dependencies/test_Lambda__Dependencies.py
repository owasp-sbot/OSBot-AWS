from unittest                                                           import TestCase
from osbot_aws.aws.lambda_.dependencies.Lambda__Dependencies            import Lambda__Dependencies
from osbot_aws.aws.lambda_.dependencies.Lambda__Dependencies__Storage   import Lambda__Dependencies__Storage


class test_Lambda__Dependencies(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.lambda_dependencies = Lambda__Dependencies()

    def test__init__(self):
        with self.lambda_dependencies as _:
            assert type(_                     ) is Lambda__Dependencies
            assert type(_.dependencies_storage) is Lambda__Dependencies__Storage