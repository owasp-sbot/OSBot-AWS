from osbot_utils.utils.Lists import list_index_by

from osbot_aws.aws.route_53.Route_53 import Route_53
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self


class Route_53__Hosted_Zone(Kwargs_To_Self):
    route_53       : Route_53
    hosted_zone_id : str


    def a_records(self):
        records = self.record_sets(group_by='Type').get('A')
        return list_index_by(records, 'Name')

    def info(self):
        raw_hosted_zone = self.route_53.hosted_zone(hosted_zone_id=self.hosted_zone_id)
        return raw_hosted_zone.get('HostedZone')

    def record_sets(self, **kwargs):
        return self.route_53.record_sets(hosted_zone_id=self.hosted_zone_id, **kwargs)




