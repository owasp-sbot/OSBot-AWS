import base64
from unittest import TestCase

from osbot_utils.utils import Png

from osbot_aws.OSBot_Setup import OSBot_Setup
from osbot_utils.utils.Dev import Dev

from osbot_aws.apis.IAM import IAM


class Test_Helper(TestCase):


    def setUp(self) -> OSBot_Setup:
        return self.osbot_setup()

    def osbot_setup(self,profile_name = None, account_id=None, region=None) -> OSBot_Setup:
        self.result   = None
        self.png_data = None
        self.png_file = '/tmp/unit-test.png'
        return OSBot_Setup(profile_name=profile_name, account_id=account_id, region_name=region)#.setup_test_environment()

    def tearDown(self):
        if self.result is not None:
            Dev.pprint(self.result)

        Png.save_png_base64_to_file(self.png_data, self.png_file)

    def check_aws_token(self):
        result = IAM().check_aws_security_tokens()
        if result.get('status') == 'Error':
            raise Exception(result['error'])
        return

    def lambda_package(self, lambda_name, profile_name = None, account_id=None, region=None):
        return self.osbot_setup(profile_name=profile_name,account_id=account_id,region=region).lambda_package(lambda_name)

    @staticmethod
    def print(result):
        if result is not None:
            Dev.pprint(result)

    @staticmethod
    def save_png(png_data, target_file):
        if png_data is not None:
            with open(target_file, "wb") as fh:
                fh.write(base64.decodebytes(png_data.encode()))
