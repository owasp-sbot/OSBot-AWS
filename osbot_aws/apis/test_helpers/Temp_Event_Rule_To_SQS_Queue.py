from osbot_aws.apis.test_helpers.Temp_Event_Rule import Temp_Event_Rule
from osbot_aws.apis.test_helpers.Temp_SQS_Queue import Temp_SQS_Queue


class Temp_Event_Rule_To_SQS_Queue:

    def __init__(self, event_source=None):
        self.sqs_queue    = None
        self.event_rule   = None
        self.target_id    = None
        self.event_source = event_source

    def __enter__(self):
        self.temp_sqs_queue  = Temp_SQS_Queue()
        self.temp_event_rule = Temp_Event_Rule(event_source=self.event_source)
        self.sqs_queue       = self.temp_sqs_queue.__enter__()
        self.event_rule      = self.temp_event_rule.__enter__()
        self.target_id       = self.event_rule.add_target_sqs_queue(self.sqs_queue)
        return self

    def __exit__(self, type, value, traceback):
        self.event_rule.delete_target(target_id=self.target_id)
        self.temp_sqs_queue .__exit__(type, value, traceback)
        self.temp_event_rule.__exit__(type, value, traceback)