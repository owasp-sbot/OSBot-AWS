from unittest import TestCase

import boto3
import botocore
import pytest

from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.apis.STS import STS

from osbot_aws.apis.Session import Session
from osbot_aws.apis.test_helpers.Temp_IAM_User import Temp_IAM_User
from osbot_aws.exceptions.Session_Client_Creation_Fail import Session_Client_Creation_Fail
from osbot_aws.helpers.boto3.View_Boto3_Rest_Calls import View_Boto3_Rest_Calls, print_boto3_calls
from osbot_utils.testing.Hook_Method import Hook_Method
from osbot_utils.testing.Unit_Test import Unit_Test
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import log_to_console, logger_set_level_debug, list_contains
from osbot_utils.utils.Status import status_ok, logger


class test_Session(TestCase):

    def setUp(self):
        #STS().check_current_session_credentials()
        #log_to_console(level=20)
        self.session = Session()
        #boto3.set_stream_logger(level=10)
        #botocore.set_stream_logger(level=10)

    def test_botocore_session(self):
        session = self.session.botocore_session()
        #pprint(session.profile)
        credentials = self.session.credentials()
        # todo add asserts of credentials when compared with
        # 'access_key',
        # 'get_frozen_credentials',
        # 'method',
        # 'secret_key',
        # 'token'
        pprint(session)

    @print_boto3_calls
    def test_credentials_ok__hook__BaseClient(self):
        #with View_Boto_3_Rest_Calls():
            self.session.credentials_ok()
            self.session.session().client('s3').list_buckets()
            self.session.credentials_ok()
            self.session.credentials_ok()
            self.session.session().client('s3').list_buckets()




    # def test_client(self):
    #     with self.assertRaises(Session_Client_Creation_Fail):
    #         self.session.client('aaaa')
    #     assert type(self.session.client('s3')).__name__ == 'S3'
    #
    # def test_client_boto3(self):
    #     #AWS_Config().set_aws_session_profile_name('bad_profile')
    #     status = self.session.client_boto3('s3')
    #     client = status.get('data').get('client')       # get client from result
    #     assert type(client).__name__ == 'S3'            # confirm is S3 class
    #     assert callable(client.list_buckets)            # config function exists
    #
    # def test_profiles(self):
    #     profiles = self.session.profiles()      # todo add method to create temp profile location
    #     if len(set(profiles)) >0:
    #         pass                        # todo: add tests when there are credentials configured at ~/.aws/credentials
    #
    #     pprint(profiles)
    #     # assert set(self.session.profiles().get('default')) == {'aws_access_key_id', 'aws_secret_access_key', 'region'}
    #
    # def test_resource(self):
    #     #with self.assertRaises(Session_Client_Creation_Fail):
    #     #    self.session.resource('aaaa')
    #     s3_resource = self.session.resource('s3')
    #     assert type(s3_resource).__name__ == 's3.ServiceResource'
    #     assert callable(s3_resource.Bucket)
    #
    # def test_session_default(self):
    #     session = self.session.session_default()
    #
    #     #todo add methods for the files below
    #     profile_name
    #     region_name
    #     pprint(type(session) == Session)
    #     pprint(session.get_available_regions(service_name="s3"))
    #     pprint(session.available_profiles)
    #     pprint(session.get_available_services())
    #     pprint(dir(session.get_credentials()))
    #     pprint(session.get_available_partitions())
    #
    #     pprint(session.SESSION_VARIABLES)
    #     pprint(dir(session))
    #
    # #@pytest.mark.skip('Fix test')
    # def test_session_custom_user(self):
    #
    #     assert self.session.session().region_name  == AWS_Config().aws_session_region_name()
    #
    #     with Temp_IAM_User() as temp_user:
    #         iam       = temp_user.iam
    #         user_info = iam.user_info()
    #
    #         access_key = iam.user_access_key_create(wait_for_key_working=True)
    #
    #         assert access_key is not None                               # None means the user_access_key_create failed
    #         aws_access_key_id     = access_key.get('AccessKeyId')
    #         aws_secret_access_key = access_key.get('SecretAccessKey')
    #
    #         session = boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    #         user_identity = session.client('sts').get_caller_identity()
    #
    #         assert user_identity.get('Account' ) == self.session.account_id
    #         assert user_identity.get('UserId'  ) == user_info.get('UserId')
    #         assert user_identity.get('Arn'     ) == user_info.get('Arn')
    #         self.result = user_identity


        #self.result = temp_user.iam.users_by_username()

        # iam = IAM(user_name=temp_user)
        # iam.user_create()
        # self.result = iam.user_info()
        # self.result = iam.users_by_username()
        # iam.user_delete()
        # self.result = iam.users_by_username()

        # session = boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        # # return session.client('sts').get_caller_identity()
        # return self.iam.account_id()
        # return self.iam.user_info()
        # return session.client('iam').get_user(UserName=self.aws_user)
