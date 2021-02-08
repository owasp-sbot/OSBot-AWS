from osbot_aws.apis.Events import Events
from osbot_utils.utils.Json import json_to_str
from osbot_utils.utils.Misc import random_string, date_time_now


class Event_Rule:
    def __init__(self, rule_name=None, event_source=None, tags=None, event_bus_name=None):
        self.event_bus_name = event_bus_name
        self.event_source   = event_source or random_string(prefix='temp_event_source-')
        self.rule_name      = rule_name    or random_string(prefix='temp_event_rule-')
        self.rule_tags      = tags         or {'Name': self.event_source}
        self.events         = Events()

    def add_target_sqs_queue(self, sqs_queue):
        rule              = self.info()
        rule_name         = self.rule_name
        target_id         = sqs_queue.name()
        target_arn        = sqs_queue.arn()
        source_arn        = rule.get('Arn')
        service           = 'events.amazonaws.com'
        resource          = sqs_queue.arn()
        target_attributes = { 'SqsParameters': { 'MessageGroupId': rule_name}}
        sqs_queue.permission_add_for_service(source_arn=source_arn, service=service, resource=resource)
        self.events.target_create(rule_name=rule_name, target_id=target_id, target_arn=target_arn, target_attributes=target_attributes)
        return target_id

    def create(self):
        return self.events.rule_create(rule_name=self.rule_name, event_source=self.event_source, tags=self.rule_tags, event_bus_name=self.event_bus_name)

    def delete(self):
        return self.events.rule_delete(self.rule_name, event_bus_name=self.event_bus_name)

    def delete_target(self, target_id=None):
        return self.events.target_delete(rule_name=self.rule_name, target_id=target_id)

    def exists(self):
        return self.events.rule_exists(rule_name=self.rule_name,event_bus_name=self.event_bus_name)

    def info(self):
        return self.events.rule(rule_name=self.rule_name, event_bus_name=self.event_bus_name)

    def name(self):
        return self.rule_name

    def send_event(self, event_data):
        if type(event_data) is not str:
            event_data = json_to_str(event_data, pretty=False)
        event  = {   'Time'      : date_time_now()       ,
                     'Source'    : self.event_source,
                     "DetailType": "myTestType"     ,
                     'Detail'    : event_data       }
        return self.events.events_put([event])

    def targets(self):
        return self.events.targets(rule_name=self.rule_name, event_bus_name=self.event_bus_name)