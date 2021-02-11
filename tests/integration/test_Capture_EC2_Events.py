from unittest import TestCase

from osbot_utils.utils.Misc import wait

from osbot_aws.apis.test_helpers.Temp_Event_Rule import Temp_Event_Rule
from osbot_aws.apis.test_helpers.Temp_SQS_Queue import Temp_SQS_Queue


class test_Capture_EC2_Events(TestCase):

    def setUp(self) -> None:
        pass

    def test___enter__exit__(self):
        event_data = {"id":"event_1"}
        with Temp_SQS_Queue() as sqs_queue:
            with Temp_Event_Rule() as event_rule:
                target_id = event_rule.add_target_sqs_queue(sqs_queue)

                event_rule.send_event(event_data)
                wait(0.5)

                assert sqs_queue.size() == 1
                assert sqs_queue.pop().get('detail') == event_data

                event_rule.delete_target(target_id=target_id)