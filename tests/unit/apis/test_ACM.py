from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.ACM import ACM


class test_ACM(Test_Helper):

    def setUp(self):
        super().setUp()
        self.acm = ACM()

    def test__ctor__(self):
        assert type(self.acm).__name__ == 'ACM'

    def test_certificate(self):
        certificate_arn = self.acm.certificates()[0].get('CertificateArn')
        self.result = self.acm.certificate(certificate_arn, include_certs=True)

    def test_certificate_request(self):
        #self.result = self.acm.certificate_request('*.gw-proxy.com')
        self.result = self.acm.certificate('arn:aws:acm:eu-west-1:311800962295:certificate/1f191c3a-0214-4ef5-9f03-27cc0b46bef3')

    def test_certificates(self):
        self.result = self.acm.certificates(index_by='DomainName')