import boto3
import pytest

from osbot_aws.AWS_Config import AWS_Config

from osbot_aws.apis.Session import Session
from osbot_aws.apis.test_helpers.Temp_User import Temp_User
from osbot_utils.testing.Unit_Test import Unit_Test


class test_Session(Unit_Test):

    def setUp(self):
        super().setUp()
        self.session = Session()

    def test_client(self):
        assert self.session.client('aaaa') is None
        assert type(self.session.client('s3')).__name__ == 'S3'

    def test_client_boto3(self):
        assert "Unknown service: 'aaaa'. Valid service names are:" in self.session.client_boto3('aaaa').get('data')
        AWS_Config().set_aws_session_profile_name('bad_profile')
        assert type(self.session.client_boto3('s3').get('client')).__name__ == 'S3'
        AWS_Config().set_aws_session_profile_name('default')

    def test_profiles(self):
        profiles = self.session.profiles()
        if len(set(profiles)) >0:
            pass                        # todo: add tests when there are credentials configured at ~/.aws/credentials


        #assert set(self.session.profiles().get('default')) == {'aws_access_key_id', 'aws_secret_access_key', 'region'}

    @pytest.mark.skip('Fix test')
    def test_session(self):
        assert self.session.session().profile_name == AWS_Config().aws_session_profile_name()
        assert self.session.session().region_name  == AWS_Config().aws_session_region_name()

        with Temp_User() as temp_user:
            iam       = temp_user.iam
            user_info = iam.user_info()

            access_key = iam.user_access_key_create(wait_for_key_working=True)

            aws_access_key_id     = access_key.get('AccessKeyId')
            aws_secret_access_key = access_key.get('SecretAccessKey')

            session = boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
            user_identity = session.client('sts').get_caller_identity()

            assert user_identity.get('UserId'  ) == user_info.get('UserId')
            assert user_identity.get('Arn'     ) == user_info.get('Arn')
            self.result = user_identity

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
