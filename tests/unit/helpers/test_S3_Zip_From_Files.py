from unittest import TestCase

from osbot_utils.utils.Dev import pprint

from osbot_aws.helpers.S3_Zip_From_Files import S3_Zip_From_Files
from osbot_utils.utils.Zip import zip_bytes_file_list


class test_S3_Zip_From_Files(TestCase):

    def setUp(self):
        pass

    def test__init____enter____default_values(self):
        with S3_Zip_From_Files() as _:
            assert _.file_name.startswith('temp_zip_file_') is True
            assert _.s3_bucket == _.aws_config.lambda_s3_bucket()
            assert _.s3_prefix == 'lambdas/unit_tests/temp_zips'
            assert _.s3_key    == f'{_.s3_prefix}/{_.file_name}.zip'

            # _.add_file_from_content('file_1.txt', 'content 1')
            # pprint(_.zip_bytes_files())


    def test_s3_file_exists(self):
        file_name = 'test_s3_file_exists'
        with S3_Zip_From_Files(file_name=file_name) as _:
            _.add_file_from_content('file_1.txt', 'content 1')
            assert _.s3_file_exists() is False
            assert _.s3_key == f'lambdas/unit_tests/temp_zips/{file_name}.zip'
            assert _.s3_file_create() is True
            assert _.s3_file_exists() is True
            assert _.s3_file_contents() == _.zip_bytes()
            assert zip_bytes_file_list(_.s3_file_contents()) == ['file_1.txt']
            assert _.s3_file_delete() is True
            assert _.s3_file_exists() is False
