import pytest
from unittest                                                                   import TestCase
from osbot_aws.AWS_Config                                                       import AWS_Config
from osbot_aws.aws.s3.S3__DB_Base                                               import S3__DB_Base
from osbot_utils.utils.Misc                                                     import list_set
from osbot_aws.aws.s3.S3__Virtual_Storage                                       import Virtual_Storage__S3, VIRTUAL_STORAGE__DEFAULT__ROOT_FOLDER


# todo add support for using localstack in these tests
class test_Virtual_Storage__S3(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.aws_config = AWS_Config()
        cls.account_id = cls.aws_config.account_id()
        #myfeeds_tests__setup_local_stack()
        cls.virtual_storage = Virtual_Storage__S3()


    def test__init__(self):
        with self.virtual_storage as _:
            assert type(_) is Virtual_Storage__S3
            assert _.root_folder == "s3-virtual-storage/" == VIRTUAL_STORAGE__DEFAULT__ROOT_FOLDER

        with self.virtual_storage.s3_db as _:
            assert type(_)       is S3__DB_Base
            assert _.s3_bucket() == f"unknown-service-{self.account_id}-osbot-aws"

    def test_get_s3_key(self):
        with self.virtual_storage as _:
            assert _.get_s3_key('abc') == f'{VIRTUAL_STORAGE__DEFAULT__ROOT_FOLDER}abc'

    def test_json__save(self):
        with self.virtual_storage as _:
            if _.s3_db.bucket_exists() is False:
                pytest.skip("test needs bucket")                    # todo: add support for localstack with this bucket setup
            path = 'pytest/an-file.json'
            data = {'a': 42}
            result = _.json__save(path=path, data=data)
            assert result is True
            assert _.file__exists(path   ) is True
            assert _.json__load(path=path) == data
            assert _.file__delete(path   ) is True
            assert _.file__exists(path   ) is False

    def test_files(self):
        with self.virtual_storage as _:
            if _.s3_db.bucket_exists() is False:
                pytest.skip("test needs bucket")                    # todo: add support for localstack with this bucket setup
            cache_index = _.json__load('llm-cache/data/cache_index.json')
            if cache_index:
                assert list_set(cache_index) == ['cache_id__from__hash__request', 'cache_id__to__file_path']





