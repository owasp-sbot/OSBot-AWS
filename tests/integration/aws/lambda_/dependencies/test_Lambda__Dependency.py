from unittest                                                                   import TestCase
from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency                      import Lambda__Dependency
from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency__Local import Lambda__Dependency__Local
from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency__S3 import Lambda__Dependency__S3
from tests.integration.aws.lambda_.dependencies.test_Lambda__Dependency__Local  import LAMBDA_DEPENDENCY__SMALL_TEST__PACKAGE
from tests.integration.osbot_aws__objs_for__integration_tests                   import setup__osbot_aws__integration_tests


class test_Lambda__Dependency(TestCase):

    @classmethod
    def setUpClass(cls):
        setup__osbot_aws__integration_tests()
        cls.package_name      = LAMBDA_DEPENDENCY__SMALL_TEST__PACKAGE
        cls.lambda_dependency = Lambda__Dependency(package_name=cls.package_name)

    def test__init__(self):
        with self.lambda_dependency as _:
            assert type(_) is Lambda__Dependency
            assert type(_.dependency__local)        is Lambda__Dependency__Local
            assert type(_.dependency__s3   )        is Lambda__Dependency__S3
            assert _.package_name                   == self.package_name
            assert _.dependency__local.package_name == self.package_name
            assert _.dependency__s3.package_name    == self.package_name