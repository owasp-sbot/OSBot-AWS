import os
import unittest

from osbot_aws.tmp_utils.Temp_Misc import Temp_Misc

from osbot_aws.apis.S3 import S3


class Test_S3(unittest.TestCase):
    def setUp(self):
        self.s3 = S3()
        assert self.s3.__class__.__name__ == 'S3'
        self.temp_file_name     = "aaa.txt"
        self.temp_file_contents = "some contents"
        self.test_bucket        = "gs-lambda-tests"
        self.test_folder        = "unit_tests"

    def _test_file(self):
        temp_file = os.path.abspath(self.temp_file_name)
        with open(temp_file, "w+") as f:
            f.write(self.temp_file_contents)
        assert os.path.isfile(temp_file) is True
        return temp_file

    def test_bucket_create_delete(self):
        bucket_name = Temp_Misc.random_text('temp_bucket').lower().replace('_','-')
        bucket_url  = 'http://{0}.s3.amazonaws.com/'.format(bucket_name)
        region      = 'eu-west-2'
        assert self.s3.bucket_exists(bucket_name) is False
        assert self.s3.bucket_create(bucket_name, region) == { 'status':'ok', 'data':bucket_url}
        assert self.s3.bucket_exists(bucket_name) is True
        assert self.s3.bucket_delete(bucket_name) is True
        assert self.s3.bucket_exists(bucket_name) is False

    def test_buckets(self):
        names = self.s3.buckets()
        assert self.test_bucket in names
        assert len(names) > 6

    @unittest.skip("find better search target")
    def test_find_files    (self):
        prefix      = 'unit_tests'
        find_filter = 'dev'
        files       = self.s3.find_files(self.test_bucket, prefix, find_filter)
        assert len(files) > 0


    def test_file_contents_delete_exists_upload   (self):
        key       = os.path.join(self.test_folder, self.temp_file_name)             # key is folder + file
        bucket    = self.test_bucket                                                # target bucket
        temp_file = self._test_file()                                               # create test test

        assert self.s3.file_exists(bucket, key                        ) is False    # confirm file doesn't exist (in s3)
        assert self.s3.file_upload(temp_file, bucket, self.test_folder) == key     # upload file (create it in s3)
        assert self.s3.file_exists(bucket, key                        ) is True     # confirm file exists (in s3)

        assert self.s3.file_contents(bucket, key) == self.temp_file_contents        # confirm file contents are expected

        assert self.s3.file_delete(bucket, key                        ) is True     # delete file
        assert self.s3.file_exists(bucket, key                        ) is False    # confirm file doesn't exist (in s3)

        os.remove(temp_file)                                                        # delete test file

    def test_file_create_from_string(self):
        file_contents = 'some test'
        bucket        = self.test_bucket                                                        # target bucket
        key           = os.path.join(self.test_folder, 'some-temp-file.txt')                    # key is folder + file

        assert self.s3.file_exists            (bucket, key               ) is False             # confirm file doesn't exist in s3
        assert self.s3.file_create_from_string(file_contents, bucket, key) is True              # create file in s3 (from string)
        assert self.s3.file_exists            (bucket, key               ) is True              # confirm file exists
        assert self.s3.file_contents          (bucket, key               ) == file_contents     # confirm file contents match
        assert self.s3.file_delete            (bucket, key               ) is True              # delete file

    def test_file_move(self):
        file_contents = 'some test'

        src_bucket  = self.test_bucket
        src_key     = self.test_folder + '/src_file.txt'
        dest_bucket = self.test_bucket
        dest_key    = self.test_folder + '/dest_file.txt'

        assert self.s3.file_create_from_string(file_contents, src_bucket, src_key              ) is True

        assert self.s3.file_exists            (src_bucket   , src_key                          ) is True
        assert self.s3.file_exists            (dest_bucket  , dest_key                         ) is False

        assert self.s3.file_move              (src_bucket   , src_key   , dest_bucket, dest_key) is True

        assert self.s3.file_exists            (src_bucket   , src_key                          ) is False
        assert self.s3.file_exists            (dest_bucket  , dest_key                         ) is True

        assert self.s3.file_contents          (dest_bucket  , dest_key                         ) == file_contents
        assert self.s3.file_delete            (src_bucket   , src_key                          ) is True
        assert self.s3.file_delete            (dest_bucket  , dest_key                         ) is True