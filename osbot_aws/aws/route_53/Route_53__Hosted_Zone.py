from osbot_aws.aws.route_53.Route_53 import Route_53
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self


class Route_53__Hosted_Zone(Kwargs_To_Self):
    route_53       : Route_53()
    hosted_zone_id : str

