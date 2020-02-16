from gw_bot.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.ACM import ACM


class test_ACM(Test_Helper):

    def setUp(self):
        super().setUp()
        self.acm = ACM()

    def test__ctor__(self):
        assert type(self.acm).__name__ == 'ACM'

    def test_certificates(self):
        self.result = self.acm.certificates(index_by='DomainName')