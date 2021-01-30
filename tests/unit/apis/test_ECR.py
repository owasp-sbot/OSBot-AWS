from unittest import TestCase

from osbot_aws.apis.STS import STS
from osbot_utils.utils.Dev import Dev, pprint

from osbot_aws.apis.ECR import ECR


class test_ECR(TestCase):

    def setUp(self) -> None:
        #STS().check_current_session_credentials()
        self.ecr = ECR()
        print()

    def test_init_(self):
        from osbot_aws.apis.S3 import S3
        pprint(S3().buckets())



