from unittest                                                                   import TestCase
from osbot_aws.aws.lambda_.schemas.Safe_Str__File__Path__Python_Package         import Safe_Str__File__Path__Python_Package
from osbot_utils.utils.Zip                                                      import zip_bytes__add_file, zip_bytes_empty, zip_bytes__files
from osbot_aws.AWS_Config                                                       import AWS_Config
from osbot_aws.aws.s3.S3                                                        import S3
from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency__S3                  import Lambda__Dependency__S3
from tests.integration.aws.lambda_.dependencies.test_Lambda__Dependency__Local  import LAMBDA_DEPENDENCY__SMALL_TEST__PACKAGE
from tests.integration.osbot_aws__objs_for__integration_tests                   import setup__osbot_aws__integration_tests

class test_Lambda__Dependency__S3(TestCase):

    @classmethod
    def setUpClass(cls):
        setup__osbot_aws__integration_tests()
        cls.package_name         = LAMBDA_DEPENDENCY__SMALL_TEST__PACKAGE
        cls.lambda_dependency_s3 = Lambda__Dependency__S3(package_name=cls.package_name)

    def test__init__(self):
        with self.lambda_dependency_s3 as _:
            assert type(_            )             is Lambda__Dependency__S3
            assert type(_.aws_config )             is AWS_Config
            assert type(_.s3         )             is S3
            assert type(_.s3.client()).__module__  == 'botocore.client'         # confirm it is a boto3 S3 client
            assert type(_.s3.client()).__name__    == 'S3'
            assert _.s3.client().meta.endpoint_url == 'http://localhost:4566'   # wired up to LocalStack
            assert self.package_name               == 'colorama==0.4.6'
            assert _.package_name                  == 'colorama==0.4.6'

    def test__1__setup(self):
        with self.lambda_dependency_s3 as _:
            assert _.setup()          == _
            assert _.bucket__exists() is True

    def test_bucket__name(self):
        with self.lambda_dependency_s3 as _:
            assert _.bucket__name() == '000000000000--osbot-lambdas--us-east-1'     # default account and region values are assigned in setup__osbot_aws__integration_tests()

    def test_file_path(self):
        with self.lambda_dependency_s3.path() as _:
            assert _       == 'lambdas-dependencies/colorama==0.4.6.zip'
            assert type(_) == Safe_Str__File__Path__Python_Package

    def test_upload(self):
        file_1__path      = 'some/path/new_file_1.txt'
        file_1__contents  = b'some content 1'
        zipped__bytes     = zip_bytes__add_file(zip_bytes_empty() , file_1__path, file_1__contents)

        with Lambda__Dependency__S3(package_name="new_file_1") as _:
            assert _.exists()                      is False
            assert zip_bytes__files(zipped__bytes) == { 'some/path/new_file_1.txt': b'some content 1' }
            assert _.upload(zipped__bytes)         == { 'bucket'      : '000000000000--osbot-lambdas--us-east-1'                                        ,
                                                        'content_type': 'application/zip'                                                               ,
                                                        'file_bytes'  : zipped__bytes                                                                   ,
                                                        'key'         : Safe_Str__File__Path__Python_Package('lambdas-dependencies/new_file_1.zip'),
                                                        'metadata'    : { 'created_by': 'osbot_aws.aws.s3.S3.file_upload_from_bytes'                    ,
                                                                          'data_type' : 'zip-folder-for-lambda-function'                                }}
            assert _.bytes() == zipped__bytes
            assert _.metadata()                     == { 'created_by': 'osbot_aws.aws.s3.S3.file_upload_from_bytes'                    ,
                                                         'data_type' : 'zip-folder-for-lambda-function'                                }
            assert _.exists()                       is True
            assert _.delete()                       is True
