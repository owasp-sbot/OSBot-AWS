from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.Route_53 import Route_53


class test_ACM(Test_Helper):

    def setUp(self):
        super().setUp()
        self.route_53 = Route_53()

    def test__ctor__(self):
        assert type(self.route_53).__name__ == 'Route_53'

    def test_record_set_upsert(self):
        name                = '*.gw-proxy.com.'
        record_type         = 'A'
        dns_name            = 'd-noho75bpih.execute-api.eu-west-1.amazonaws.com.'
        hosted_zone_id      = '/hostedzone/ZMHOWKWA1ZN69'
        alias_hosted_zone_id = 'ZLY8HYME6SFDD'
        self.result = self.route_53.record_set_upsert(name, record_type, dns_name,hosted_zone_id,alias_hosted_zone_id)

    def test_record_sets(self):
        hosted_zone = '/hostedzone/ZMHOWKWA1ZN69'
        self.result = self.route_53.record_sets(hosted_zone, group_by='Name')

    def test_domains(self):
        self.result = self.route_53.domains(index_by='DomainName')

    def test_hosted_zones(self):
        assert 'gw-proxy.com.' in self.route_53.hosted_zones(index_by='Name')
        assert None            in self.route_53.hosted_zones(index_by='aaa')
        assert self.route_53.hosted_zones(index_by=None) == self.route_53.hosted_zones()
        assert set(self.route_53.hosted_zones()[0]) == {'CallerReference', 'Config', 'Name', 'Id', 'ResourceRecordSetCount'}


