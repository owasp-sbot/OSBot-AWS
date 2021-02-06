from osbot_aws.apis.Events import Events
from osbot_aws.helpers.Event_Rule import Event_Rule
from osbot_utils.utils.Misc import random_string


class Temp_Event_Rule:

    def __init__(self, rule_name=None, event_source=None, tags=None, event_bus_name=None):
        self.event_rule = Event_Rule(rule_name=rule_name, event_source=event_source, tags=tags, event_bus_name=event_bus_name)

    def __enter__(self):
        self.event_rule.create()
        return self.event_rule


    def __exit__(self, type, value, traceback):
        self.event_rule.delete()
