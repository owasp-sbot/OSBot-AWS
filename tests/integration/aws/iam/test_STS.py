import pytest
from unittest                       import TestCase
from osbot_utils.utils.Dev          import pprint
from osbot_aws.aws.iam.IAM_Role     import IAM_Role
from osbot_aws.aws.iam.STS          import STS


@pytest.mark.skip('Wire up tests')
class test_STS(TestCase):

    def setUp(self) -> None:
        self.sts = STS()

    def test_check_current_session_credentials(self):
        self.sts.check_current_session_credentials()

    def test_assume_role_wait_until_it_works(self):
        role_name = 'osbot_temp_role_urfgvoho'
#        with Temp_IAM_Role(role_name=role_name, delete_on_exit=False) as iam_role:
#            assert iam_role.exists()
        iam_role = IAM_Role(role_name=role_name)
        pprint(iam_role.info())
            #result = self.sts.assume_role__wait_until_enabled(iam_role.role_name)
            #pprint(iam_role.role_name)
            #test_role = IAM(role_name="temp_role_to_test_assume_role")

    #def test_assume_role(self):


    #@pytest.mark.usefixtures('fixtures')                                   # todo add test that goes around the current caching that occurs in self.sts.sts()
    #def test_check_current_session_credentials__bad_credentials(self):
        #with self.monkeypatch.context() as m:
        #    m.setenv("AWS_ACCESS_KEY_ID", '')
            #print(self.sts.sts.osbot_cache_return_value__sts)
            #self.sts.check_current_session_credentials()


    # @pytest.fixture(autouse=False)
    # def fixtures(self, monkeypatch):
    #     self.monkeypatch = monkeypatch                                    # set and restore object values