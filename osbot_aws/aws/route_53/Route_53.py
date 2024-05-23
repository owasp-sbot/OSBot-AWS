from osbot_utils.decorators.lists.group_by import group_by
from osbot_utils.decorators.lists.index_by import index_by
from osbot_utils.decorators.methods.catch import catch

from osbot_aws.apis.Session            import Session


class Route_53:
    def __init__(self):
        self._route_53         = None
        self._route_53_domains = None

    @catch
    def client(self):
        if self._route_53 is None:
            self._route_53 = Session().client('route53',region_name='us-east-1')
        return self._route_53

    @catch
    def client_domains(self):
        if self._route_53_domains is None:
            self._route_53_domains = Session().client('route53domains',region_name='us-east-1')
        return self._route_53_domains

    # Main methods
    @catch
    def record_set_upsert(self, name, record_type, dns_name,hosted_zone_id,alias_hosted_zone_id):
        params = {  "HostedZoneId" : hosted_zone_id,
                    "ChangeBatch": { "Changes": [{ "Action": "UPSERT",
                                                   "ResourceRecordSet": { "Name": name,
                                                                          "Type": record_type,
                                                                          "AliasTarget": { "DNSName": dns_name,
                                                                                           "HostedZoneId": alias_hosted_zone_id,
                                                                                           "EvaluateTargetHealth": False}}}]}}

        return self.client().change_resource_record_sets(**params)


    @catch
    @group_by
    def record_sets(self, hosted_zone_id):
        return self.client().list_resource_record_sets(HostedZoneId=hosted_zone_id).get('ResourceRecordSets')

    @catch
    @index_by
    def domains(self):
        return self.client_domains().list_domains().get('Domains')

    @catch
    @index_by
    def hosted_zones(self):
        return self.client().list_hosted_zones().get('HostedZones')


