import inspect
import os
from unittest import TestCase

import botocore

from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.exceptions.Session_Client_Creation_Fail import Session_Client_Creation_Fail
from osbot_utils.utils.Objects import obj_data

from osbot_utils.utils.Files import pickle_save_to_file

from osbot_utils.utils.Functions import method_params
from osbot_utils.utils.trace.Trace_Call import trace_calls

from osbot_aws.apis.Session import Session
from osbot_aws.helpers.boto3.View_Boto3_Rest_Calls import print_boto3_calls
from osbot_utils.utils.Dev import pprint
from tests.integration.aws.iam.test_IAM import IAM_USER_NAME__OSBOT_AWS


#from osbot_utils.utils.trace.


class test_Session(TestCase):

    def setUp(self):
        self.aws_config = AWS_Config()
        #STS().check_current_session_credentials()
        #log_to_console(level=20)

        self.session = Session()
        #boto3.set_stream_logger(level=10)
        #botocore.set_stream_logger(level=10)

    def test___init__(self):
        assert self.session.__default_kwargs__() == {'account_id': None, 'profile_name': None, 'region_name': None}
        assert self.session.__kwargs__        () == {'account_id': os.getenv('AWS_ACCOUNT_ID'), 'profile_name': os.getenv('AWS_PROFILE_NAME'), 'region_name': os.getenv('AWS_DEFAULT_REGION')}
        assert self.session.__locals__        () == { 'aws_config': self.session.aws_config, **self.session.__kwargs__() }
        assert self.session.aws_config.__class__.__name__ == 'AWS_Config'

    def test_boto_session(self):
        boto_session = self.session.boto_session()
        assert type(boto_session) == botocore.session.Session

    #@print_boto3_calls
    # @trace_calls(include=['*'], show_parent=True, show_duration=True,
    #              duration_bigger_than=0.01,
    #              locals=False)
    def test_botocore_session(self):
        assert method_params(self.session.botocore_session) == { 'args'  : [],
                                                                 'kwargs': { 'aws_access_key_id'    : None,
                                                                             'aws_secret_access_key': None,
                                                                             'aws_session_token'    : None,
                                                                             'botocore_session'     : None,
                                                                             'profile_name'         : None,
                                                                             'region_name'          : None}}

        botocore_session = self.session.botocore_session()
        assert botocore_session.region_name == self.aws_config.aws_session_region_name()

    def test_caller_identity(self):
        caller_identity = self.session.caller_identity()
        assert caller_identity.get('Account' ) == self.session.account_id
        assert caller_identity.get('Arn'     ) == f'arn:aws:iam::{self.session.account_id}:user/{IAM_USER_NAME__OSBOT_AWS}'
        assert caller_identity.get('UserId'  ).__class__.__name__ == 'str'

    #@print_boto3_calls
    def test_credentials_ok(self):
        self.session.credentials_ok()



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
