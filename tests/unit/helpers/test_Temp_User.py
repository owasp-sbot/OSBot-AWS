from osbot_aws.apis.IAM import IAM
from osbot_aws.helpers.Temp_User import Temp_User
from osbot_utils.testing.Unit_Test import Unit_Test


class test_Temp_User(Unit_Test):

    def test__init__(self):
        temp_name = Temp_User().user_name
        assert len(temp_name) == 16
        assert temp_name.startswith('temp_user_')
        assert IAM(user_name=temp_name).user_exists() is False

    def test_enter_exit(self):
        with Temp_User() as temp_user:
            self.result = temp_user.iam.user_exists()                                   # inside `with block` user should exist
            assert temp_user.iam.user_exists() is True
            user_info = temp_user.iam.user_info()
            assert user_info.get('UserName') == temp_user.user_name
            assert f'arn:aws:iam::{temp_user.iam.account_id()}:user/{temp_user.user_name}' == user_info.get('Arn')

        assert temp_user.iam.user_exists() is False                                     # outside `with block` user should not exist
