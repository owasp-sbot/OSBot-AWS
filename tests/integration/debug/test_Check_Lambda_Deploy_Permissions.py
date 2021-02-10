from unittest import TestCase

from osbot_utils.utils.Files import folder_files, files_list, path_combine, file_exists

from osbot_aws.deploy.Deploy_Lambda import Deploy_Lambda

from osbot_aws.lambdas.dev.hello_world import run

from osbot_utils.utils.Misc import random_string

from osbot_aws.AWS_Config import AWS_Config

from osbot_aws.apis.S3 import S3

from osbot_aws.apis.Lambda import Lambda
from osbot_aws.apis.STS import STS
from osbot_utils.utils.Dev import pprint


class test_Check_Lambda_Deploy_Permissions(TestCase):

    def setUp(self):
        self.aws_config  = AWS_Config()
        self.lambda_     = Lambda()
        self.s3          = S3()
        self.sts         = STS()

        self.expected_account_id = '785217600689'
        self.expected_region     = 'eu-west-1'
        self.expected_s3_prefix  = 'lambdas'
        self.expected_role_name  = None
        self.expected_s3_bucket  = f'{self.expected_account_id}-osbot-{self.expected_s3_prefix}'


    def test_aws_config(self ):
        assert self.aws_config.aws_session_account_id()  == self.expected_account_id
        assert self.aws_config.aws_session_region_name() == self.expected_region
        assert self.aws_config.lambda_role_name()        == self.expected_role_name
        assert self.aws_config.lambda_s3_key_prefix()    == self.expected_s3_prefix
        assert self.aws_config.lambda_s3_bucket()        == self.expected_s3_bucket

    def test_check_sts_credentials(self):
        assert self.sts.caller_identity_account()           == '785217600689'
        assert self.sts.check_current_session_credentials() is True
        assert self.sts.current_region_name()               == self.expected_region

    def test_s3_read_access(self):
        expected_file   = 'lambdas/k8_live_servers.lambdas.screenshot.zip'
        buckets         = self.s3.buckets()
        files_in_bucket = self.s3.find_files(self.expected_s3_bucket, self.expected_s3_prefix)

        assert len(buckets)            > 0
        assert self.expected_s3_bucket in buckets
        assert len(files_in_bucket)    > 0
        assert expected_file           in files_in_bucket

    def test_s3_write_access(self):
        temp_contents  = random_string(length=1024)
        temp_file_name = f"{random_string()}_temp_file.txt"
        bucket         = self.expected_s3_bucket
        temp_s3_key    = f'{self.expected_s3_prefix}/{temp_file_name}'

        assert self.s3.file_exists(bucket=bucket, key=temp_s3_key) is False
        self.s3.file_create_from_string(file_contents=temp_contents, bucket=bucket, key=temp_s3_key)
        assert self.s3.file_delete(bucket=bucket, key=temp_s3_key) is True
        assert self.s3.file_exists(bucket=bucket, key=temp_s3_key) is False

    def test_lambda_upload_file(self):
        lambda_handler = run
        deploy_lambda  = Deploy_Lambda(lambda_handler)
        package        = deploy_lambda.package
        aws_lambda     =  package.aws_lambda

        deploy_lambda.add_function_source_code()

        assert run.__module__                          == 'osbot_aws.lambdas.dev.hello_world'
        assert run.__name__                            == 'run'
        assert '/osbot_aws/lambdas/dev/hello_world.py' in package.get_files()
        assert len(files_list(aws_lambda.folder_code)) == len(package.get_files())
        assert file_exists(path_combine(aws_lambda.folder_code, 'osbot_aws/lambdas/dev/hello_world.py'))

        assert aws_lambda.s3_bucket == '785217600689-osbot-lambdas'
        assert aws_lambda.s3_key    == 'lambdas/osbot_aws.lambdas.dev.hello_world.zip'

        assert self.s3.file_exists(bucket=aws_lambda.s3_bucket, key=aws_lambda.s3_key) is True
        assert self.s3.file_delete(bucket=aws_lambda.s3_bucket, key=aws_lambda.s3_key) is True
        assert self.s3.file_exists(bucket=aws_lambda.s3_bucket, key=aws_lambda.s3_key) is False



