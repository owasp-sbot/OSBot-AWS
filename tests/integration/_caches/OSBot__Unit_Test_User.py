from osbot_aws.aws.iam.IAM_User import IAM_User
from osbot_utils.base_classes.Kwargs_To_Disk import Kwargs_To_Disk

OSBOT__TEST__USER_NAME = 'OSBot__Unit_Test_User'

class OSBot__Unit_Test_User(Kwargs_To_Disk):
    _user       : IAM_User
    setup       : bool
    user_exists : bool
    user_info   : dict
    user_name   : str

    def __init__(self):
        super().__init__()
        self.setup_user()

    def user_id(self):
        return self.user_info.get('UserId')

    def setup_user(self):
        if self.user_name is None:
            self.user_name   = OSBOT__TEST__USER_NAME
            self.setup = False

        self._user       = IAM_User(self.user_name)

        if self.user_exists is not True:
            self.user_info  = self._user.create()
            self.user_exists = self._user.exists()
            self.setup = True