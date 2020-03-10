from gw_bot.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.test_helpers.Temp_S3_Zip_With_Lambda_File import Temp_S3_Zip_With_Lambda_File


class test_Temp_S3_Zip_With_Lambda_File(Test_Helper):
    def setUp(self):
        super().setUp()

    def test_file_create_and_deletion(self):
        with Temp_S3_Zip_With_Lambda_File() as temp_zip:
            self.result = temp_zip