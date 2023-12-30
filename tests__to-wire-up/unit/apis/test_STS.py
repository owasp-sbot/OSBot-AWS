from unittest import TestCase

import pytest

from osbot_aws.apis.STS import STS


class test_STS(TestCase):

    def setUp(self) -> None:
        self.sts = STS()

    def test_check_current_session_credentials(self):
        self.sts.check_current_session_credentials()

    #@pytest.mark.usefixtures('fixtures')                                   # todo add test that goes around the current caching that occurs in self.sts.sts()
    #def test_check_current_session_credentials__bad_credentials(self):
        #with self.monkeypatch.context() as m:
        #    m.setenv("AWS_ACCESS_KEY_ID", '')
            #print(self.sts.sts.osbot_cache_return_value__sts)
            #self.sts.check_current_session_credentials()


    # @pytest.fixture(autouse=False)
    # def fixtures(self, monkeypatch):
    #     self.monkeypatch = monkeypatch                                    # set and restore object values