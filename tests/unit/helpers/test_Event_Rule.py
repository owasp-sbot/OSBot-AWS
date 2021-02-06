from unittest import TestCase

from osbot_aws.apis.test_helpers.Temp_SQS_Queue import Temp_SQS_Queue
from osbot_aws.decorators.aws_inject import aws_inject
from osbot_aws.helpers.Event_Rule import Event_Rule
from osbot_utils.utils.Dev import pprint


class test_Event_Rule(TestCase):

    event_rule = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.event_rule = Event_Rule()
        assert cls.event_rule.exists() is False
        cls.rule_arn = cls.event_rule.create()
        assert cls.event_rule.exists() is True
        assert cls.event_rule.info().get('Arn') == cls.rule_arn

    @classmethod
    def tearDownClass(cls) -> None:
        assert cls.event_rule.delete() is True

    def setUp(self) -> None:
        pass

    @aws_inject('account_id,region')
    def test_create(self, account_id, region):
        with Temp_SQS_Queue() as sqs_queue:
            assert self.event_rule.targets() == []
            rule_name  = self.event_rule.name()
            queue_name = sqs_queue.name()
            target_id = self.event_rule.add_target_sqs_queue(sqs_queue)
            assert self.event_rule.targets() == [ { 'Arn'          : f'arn:aws:sqs:{region}:{account_id}:{queue_name}',
                                                    'Id'           : f'{queue_name}',
                                                    'SqsParameters': {'MessageGroupId': rule_name}}]
            pprint(self.event_rule.delete_target(target_id=target_id))



