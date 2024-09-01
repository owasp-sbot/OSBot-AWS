from os import environ
from unittest               import TestCase

from osbot_aws.aws.sts.STS  import STS
from osbot_aws.testing.TestCase__Boto3_Cache import TestCase__Boto3_Cache
from osbot_utils.utils.Dev import pprint


class test_STS(TestCase__Boto3_Cache):

    def setUp(self) -> None:
        self.sts = STS()

    def test_check_current_session_credentials(self):
        self.sts.check_current_session_credentials()


    def test_current_account_id(self):
        current_account_id = self.sts.current_account_id()
        env_account_id     = environ.get('AWS_ACCOUNT_ID')
        assert current_account_id
        if env_account_id:
            assert current_account_id == env_account_id

    #@pytest.mark.usefixtures('fixtures')                                   # todo add test that goes around the current caching that occurs in self.sts.sts()
    #def test_check_current_session_credentials__bad_credentials(self):
        #with self.monkeypatch.context() as m:
        #    m.setenv("AWS_ACCESS_KEY_ID", '')
            #print(self.sts.sts.osbot_cache_return_value__sts)
            #self.sts.check_current_session_credentials()


    # @pytest.fixture(autouse=False)
    # def fixtures(self, monkeypatch):
    #     self.monkeypatch = monkeypatch                                    # set and restore object values