import os
from unittest import TestCase

from dotenv import load_dotenv

from osbot_utils.utils.Misc import list_set, random_string

from osbot_utils.utils.Dev import pprint

from osbot_aws.apis.Cognito_IDP import Cognito_IDP


class test_Cognito_IDP(TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()

    def setUp(self) -> None:
        self.cognito        = Cognito_IDP()
        assert self.cognito_user_pool_id is not None

    def cognito_client_id(self):
        return os.environ.get("COGNITO_CLIENT_ID")

    def cognito_project(self):
        return os.environ.get("COGNITO_PROJECT")

    def cognito_region(self):
        return os.environ.get("AWS_DEFAULT_REGION")

    def cognito_user_pool_id(self):
        return os.environ.get("COGNITO_USER_POOL_ID")

    def cognito_user_name_1(self):
        return os.environ.get("COGNITO_USER_NAME_1")

    def cognito_user_pws_1(self):
        return os.environ.get("COGNITO_USER_PWD_1")

    def test_env_variables(self):
        assert self.cognito_client_id   () is not None
        assert self.cognito_project     () is not None
        assert self.cognito_region      () is not None
        assert self.cognito_user_pool_id() is not None
        assert self.cognito_user_name_1 () is not None
        assert self.cognito_user_pws_1  () is not None

    def test_user(self):
        user = self.cognito.user(self.cognito_user_pool_id(), self.cognito_user_name_1())
        assert list_set(user) == ['enabled', 'user_create_date', 'user_last_modified_date', 'user_status', 'username']

    def test_user_create__delete(self):
        email               = f'unit_test_{random_string()}@aaaaaaaaa.com'
        user_attributes     = [{'Name': 'email', 'Value': email}]
        user_name           = f'unit_test_{random_string()}'
        temporary_password  = f'123!!!@@_Aa_{random_string()}'
        user_pool_id        = self.cognito_user_pool_id()


        # create user
        user = self.cognito.user_create(user_pool_id, user_name, user_attributes, temporary_password)

        assert user.get('email') == email
        assert user.get('username') == user_name
        assert user.get('user_status') == 'FORCE_CHANGE_PASSWORD'

        # change user password
        self.cognito.user_set_password(user_pool_id, user_name, temporary_password)

        #auth initiate (i.e. login)
        result = self.cognito.auth_initiate(self.cognito_client_id() , user_name , temporary_password)
        assert list_set(result) == ['AuthenticationResult', 'ChallengeParameters']
        assert result.get('ChallengeParameters') == {}
        assert list_set(result.get('AuthenticationResult')) == ['AccessToken', 'ExpiresIn', 'IdToken', 'NewDeviceMetadata', 'RefreshToken', 'TokenType']

        try:
            user_info = self.cognito.user_info(user_pool_id, user_name)
            pprint(user_info)

            # take a look at the access token
            #access_token = result.get('AuthenticationResult').get('AccessToken')
            #decoded_access_token = jwt.decode(access_token, algorithms=["RS256"], options={"verify_signature": False})
            #pprint(decoded_access_token)


            # user create here did not had the required scope
            #response = self.cognito.auth_user_info(self.cognito_project(), self.cognito_region(), access_token)
            #pprint(response.text)

        except Exception as error:
            pprint(error)
        # delete user
        result = self.cognito.user_delete(user_pool_id, user_name)
        assert result is True

    def test_user_pool(self):
        user_pool = self.cognito.user_pool(self.cognito_user_pool_id())
        assert list_set(user_pool) == ['arn','domain','id','name','password_policy','schema','status','tags','user_count']
        assert len(user_pool.get('schema')) > 0

    def test_users(self):
        users = self.cognito.users(self.cognito_user_pool_id())
        assert len(users) > 0


