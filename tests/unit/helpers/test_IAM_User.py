from gw_bot.helpers.Test_Helper import Test_Helper
from osbot_aws.helpers.IAM_User import IAM_User


class test_IAM_User(Test_Helper):

    def setUp(self):
        super().setUp()
        self.user_name = 'aawais@glasswallsolutions.com'# 'Unit_Test_User'
        self.user = IAM_User(self.user_name)
        self.user.create()

    def tearDown(self):
        super().tearDown()
        #self.iam_user.delete()

    def test_arn(self):
        self.result = self.user.arn()

    def test_create_exists_delete(self):
        assert self.user.create().get('UserName') == self.user_name
        assert self.user.exists() is True
        assert self.user.delete() is True
        assert self.user.exists() is False

    def test_groups(self):
        self.result = self.user.groups(index_by='group_name')

    def test_id(self):
        self.result = self.user.id()

    def test_policies(self):
        self.result = self.user.policies()

    def test_roles(self):
        self.result = self.user.iam.resource().User(self.user_name)

    def test_tags(self):
        self.result = self.user.tags()
