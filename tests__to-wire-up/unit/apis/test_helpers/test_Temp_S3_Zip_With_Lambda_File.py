from osbot_utils.utils.Dev import pprint

from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.test_helpers.Temp_S3_Zip_With_Lambda_File import Temp_S3_Zip_With_Lambda_File
from osbot_utils.utils.Files import folder_exists, file_exists, folder_not_exists, file_not_exists


class test_Temp_S3_Zip_With_Lambda_File(Test_Helper):
    def setUp(self):
        super().setUp()


    def test__init__enter__exist(self):
        with Temp_S3_Zip_With_Lambda_File() as _:
            assert folder_exists(_.folder_temp)
            assert file_exists  (_.file_temp  )
            assert file_exists  (_.file_zip   )
            assert _.s3_bucket  == _.aws_config.lambda_s3_bucket()
            assert _.s3_prefix  == 'lambdas/unit_tests/temp_zips'
            assert _.s3_key     == f'{_.s3_prefix}/{_.file_name}.zip'
            assert _.file_name.startswith('temp_zip_file_') is True
            assert _.create_s3_file     is True
            assert _.s3_bucket_exists() is True
            assert _.s3_upload_ok       is True
            assert _.s3_key in _.s3_files_in_folder()


            #pprint(_.s3_file_contents())

        assert file_not_exists  (_.file_temp)
        assert file_not_exists  (_.file_zip )
        assert folder_not_exists(_.folder_temp)
        assert _.file_delete_ok is True

