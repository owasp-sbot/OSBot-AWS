from osbot_utils.utils.Dev import pprint

from osbot_utils.utils.Lists import list_index_by

from osbot_aws.aws.route_53.Route_53 import Route_53
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self


class Route_53__Hosted_Zone(Kwargs_To_Self):
    route_53       : Route_53
    hosted_zone_id : str

    def a_records(self):
        records = self.record_sets(group_by='Type').get('A')
        return list_index_by(records, 'Name')

    def create_new_a_record(self, record_name , alias_target, hosted_zone_id, alias_hosted_zone_id):
        create_kwargs = dict(record_name            = record_name          ,
                             record_type            = 'A'                  ,
                             alias_target               = alias_target     ,
                             hosted_zone_id         = hosted_zone_id       ,
                             alias_hosted_zone_id   = alias_hosted_zone_id )

        response = self.route_53.record_set__upsert(**create_kwargs)
        return response.get('ChangeInfo')

    def info(self):
        raw_hosted_zone = self.route_53.hosted_zone(hosted_zone_id=self.hosted_zone_id)
        return raw_hosted_zone.get('HostedZone')

    def record_set(self, record_name, record_type='A'):
        return self.route_53.record_set(hosted_zone_id=self.hosted_zone_id, record_name=record_name, record_type=record_type)

    def delete_record_set__a__to_alias(self, dns_entry, alias_dns_name, alias_hosted_zone_id):
        kwargs = dict(hosted_zone_id       = self.hosted_zone_id ,
                      record_name          = dns_entry         ,
                      record_type          = 'A'                 ,
                      alias_dns_name       = alias_dns_name      ,
                      alias_hosted_zone_id = alias_hosted_zone_id)
        return self.route_53.record_set__delete__alias(**kwargs).get('ChangeInfo')

    def record_sets(self, **kwargs):
        return self.route_53.record_sets(hosted_zone_id=self.hosted_zone_id, **kwargs)

    def check_dns_answer(self, record_name, record__type='A'):
        return self.route_53.check_dns_answer(hosted_zone_id=self.hosted_zone_id, record_name=record_name, record_type=record__type)




