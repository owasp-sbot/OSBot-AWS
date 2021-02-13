from unittest import TestCase

from osbot_aws.apis.test_helpers.Temp_EC2_Instance import Temp_EC2_Instance
from osbot_aws.decorators.aws_inject import aws_inject
from osbot_utils.utils.Misc import wait

from osbot_aws.apis.test_helpers.Temp_Event_Rule_To_SQS_Queue import Temp_Event_Rule_To_SQS_Queue
from osbot_utils.utils.Dev import pprint


class test_Temp_Event_Rule_To_SQS_Queue(TestCase):

    def setUp(self) -> None:
        self.event_source = 'aws.ec2' #'an_event_source'

    @aws_inject('account_id,region')
    def test___enter__exit__(self,account_id,region):
        with Temp_Event_Rule_To_SQS_Queue(event_source=self.event_source) as _:
            wait(0.6)                                   # wait for rules to activate
            with Temp_EC2_Instance() as ec2_instance:
                assert ec2_instance.exists()
            wait(2.0)                                   # todo add method to wait for events to be captured by rule and send to queue

            message_1   = _.sqs_queue.pop()
            message_2   = _.sqs_queue.pop()
            instance_id = ec2_instance.instance_id
            del message_1['time']
            del message_1['id'  ]
            del message_2['time']
            del message_2['id'  ]
            expected_message_1_state = 'pending'
            expected_message_2_state = 'shutting-down'
            assert _.event_rule.event_source == 'aws.ec2'
            assert message_1 == { 'account'    : account_id                                                      ,
                                  'detail'     : {'instance-id': instance_id, 'state': expected_message_1_state },
                                  'detail-type': 'EC2 Instance State-change Notification'                        ,
                                  'region'     : region                                                          ,
                                  'resources'  : [ f'arn:aws:ec2:{region}:{account_id}:instance/{instance_id}']  ,
                                  'source'     : 'aws.ec2'                                                       ,
                                  'version'    : '0'                                                             }
            assert message_2 == { 'account'    : account_id                                                      ,
                                  'detail'     : {'instance-id': instance_id, 'state': expected_message_2_state },
                                  'detail-type': 'EC2 Instance State-change Notification'                        ,
                                  'region'     : region                                                          ,
                                  'resources'  : [ f'arn:aws:ec2:{region}:{account_id}:instance/{instance_id}']  ,
                                  'source'     : 'aws.ec2'                                                       ,
                                  'version'    : '0'                                                             }