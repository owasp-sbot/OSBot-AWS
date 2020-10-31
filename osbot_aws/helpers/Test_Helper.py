import base64
from unittest import TestCase

from gw_bot.setup.OSBot_Setup import OSBot_Setup
from osbot_utils.utils.Dev import Dev


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
        if self.png_data is not None:
            if type(self.png_data) is not str:
                Dev.pprint(f'Png data was not a string: {self.png_data}')
            else:
                try:
                    with open(self.png_file, "wb") as fh:
                        fh.write(base64.decodebytes(self.png_data.encode()))
                    Dev.pprint(f'Png data with size {len(self.png_data)} saved to {self.png_file}')
                except Exception as error:
                    Dev.pprint(f'png save error: {error}')
                    Dev.pprint(self.png_data)

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
