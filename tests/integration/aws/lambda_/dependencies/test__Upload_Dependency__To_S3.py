from unittest                                                            import TestCase

from osbot_utils.helpers.safe_str.Safe_Str__File__Path import Safe_Str__File__Path
from osbot_utils.utils.Dev import pprint

from osbot_aws.aws.lambda_.dependencies.Lambda__Dependencies import Lambda__Dependencies
from osbot_aws.aws.lambda_.dependencies.Lambda__Upload_Dependency__To_S3 import Lambda__Upload_Dependency__To_S3
from tests.integration.osbot_aws__objs_for__integration_tests            import setup__osbot_aws__integration_tests


class test__Upload_Dependency__To_S3(TestCase):

    @classmethod
    def setUpClass(cls):
        setup__osbot_aws__integration_tests()
        cls.upload_dependency_to_s3 = Lambda__Upload_Dependency__To_S3()

    def test__init__(self):
        with self.upload_dependency_to_s3 as _:
            assert type(_               ) is Lambda__Upload_Dependency__To_S3
            assert type(_.dependencies  ) is Lambda__Dependencies
            assert type(_.path_packages ) is Safe_Str__File__Path


    # def test_install_locally(self):
    #     assert self.lambda_setup.install_locally(self.package) is True
    #     assert self.lambda_setup.exists_locally (self.package) is True
    #
    # def test_upload_to_s3(self):
    #     pprint(self.lambda_setup.    upload_to_s3(self.package))
