from gw_bot.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.test_helpers.Temp_S3_Zip_With_Lambda_File import Temp_S3_Zip_With_Lambda_File
from osbot_utils.utils.Files import Files, folder_exists, file_exists


class test_Temp_S3_Zip_With_Lambda_File(Test_Helper):
    def setUp(self):
        super().setUp()

    def test_file_create_and_deletion(self):
        with Temp_S3_Zip_With_Lambda_File() as temp_s3_zip:
            assert folder_exists(temp_s3_zip.folder)
            assert file_exists(temp_s3_zip.tmp_file)
            assert temp_s3_zip.s3_prefix == 'lambdas/unit_tests/temp_zips'
            assert 'temp_zip_file_'      in temp_s3_zip.file_name
            assert temp_s3_zip.s3_key    == f'{temp_s3_zip.s3_prefix}/{temp_s3_zip.file_name}.zip'

