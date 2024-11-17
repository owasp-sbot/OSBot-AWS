from osbot_aws.testing.TestCase__S3__Temp_Bucket import TestCase__S3__Temp_Bucket

class test_S3__bucket_versioning(TestCase__S3__Temp_Bucket):

    def test_bucket_versioning__status(self):
        bucket_name = self.temp_bucket_name
        with self.s3 as _:
            #assert _.bucket_versioning__status(bucket_name) == 'Not Enabled'
            #assert _.bucket_versioning__enable(bucket_name) is True
            assert _.bucket_versioning__status(bucket_name) == 'Enabled'

    def test__file_versions(self):
        bucket_name = self.temp_bucket_name
        with self.s3 as _:
            assert _.bucket_versioning__enable(bucket_name) is True
            key = 'file.txt'
            assert _.file_create_from_string('file content 1', bucket_name, key) is True
            assert _.file_create_from_string('file content 2', bucket_name, key) is True
            assert _.file_delete(bucket_name, key) is True
            assert _.file_create_from_string('file content 3', bucket_name, key) is True

            print()
            files_contents = []
            for file_version in _.file_versions(bucket_name, key):
                version_id = file_version.get('VersionId')

                files_contents.append(_.file_bytes(bucket_name,key, version_id=version_id))

            assert files_contents == [b'file content 3', b'file content 2', b'file content 1']



