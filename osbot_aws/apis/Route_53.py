from osbot_aws.apis.Session            import Session
from osbot_aws.helpers.Method_Wrappers import catch, index_by, group_by


class Route_53:
    def __init__(self):
        self._route_53         = None
        self._route_53_domains = None

    # Helper methods
    def _index_by(self, values, index_by=None):
        if index_by is None:
            return list(values)
        results = {}
        for item in values:
            results[item.get(index_by)] = item
        return results

    def route_53(self):
        if self._route_53 is None:
            self._route_53 = Session().client('route53',region_name='us-east-1')
        return self._route_53

    def route_53_domains(self):
        if self._route_53_domains is None:
            self._route_53_domains = Session().client('route53domains',region_name='us-east-1')
        return self._route_53_domains

    # Main methods

    def record_set_upsert(self, name, record_type, dns_name,hosted_zone_id,alias_hosted_zone_id):
        try:
            params = {  "HostedZoneId" : hosted_zone_id,
                        "ChangeBatch": { "Changes": [{ "Action": "UPSERT",
                                                       "ResourceRecordSet": { "Name": name,
                                                                              "Type": record_type,
                                                                              "AliasTarget": { "DNSName": dns_name,
                                                                                               "HostedZoneId": alias_hosted_zone_id,
                                                                                               "EvaluateTargetHealth": False}}}]}}

            return self.route_53().change_resource_record_sets(**params)
        except Exception as error:
            return { 'error' : f'{error}'}

    @catch
    @group_by
    def record_sets(self,hosted_zone):
        return self.route_53().list_resource_record_sets(HostedZoneId=hosted_zone).get('ResourceRecordSets')

    @catch
    @index_by
    def domains(self):
        return self.route_53_domains().list_domains().get('Domains')

    def hosted_zones(self, index_by=None):
        try:
            return self._index_by(self.route_53().list_hosted_zones().get('HostedZones'),index_by=index_by)
        except Exception as error:
            return {'error': f'{error}'}


