from unittest import TestCase

import pytest

from osbot_aws.decorators.aws_inject import aws_inject
from osbot_aws.helpers.SQS_Queue import SQS_Queue
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import random_string, list_set, wait

from osbot_aws.apis.SQS import SQS


class test_SQS(TestCase):

    queue = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.queue_name  = random_string(prefix='unit_tests_temp_queue-')
        cls.queue       = SQS_Queue(cls.queue_name)
        cls.queue_url   = cls.queue.create()
        assert cls.queue.exists() is True

    @classmethod
    def tearDownClass(cls) -> None:
        assert cls.queue.delete() is True

    def setUp(self) -> None:
        self.sqs = SQS()

    def test_queue_attributes(self):
        assert self.queue.attributes().get('QueueName') == self.queue_name

    def test_create(self):
        temp_queue_name = random_string(prefix='k8_unit_tests_another-temp_queue-')
        queue_url = self.sqs.queue_create(queue_name=temp_queue_name)

        assert queue_url == self.sqs.queue_url(queue_name=temp_queue_name)
        assert self.sqs.queue_exists(queue_url=queue_url) is True
        assert self.sqs.queue_delete(queue_url=queue_url) is True

    def test_create_fifo(self):
        temp_queue_name  = f"k8_unit_tests_an-fifo-temp_queue-{random_string()}.fifo"
        message_group_id = 'message_group_id'
        fifo_queue       = SQS_Queue(queue_name=temp_queue_name, message_group_id=message_group_id)
        queue_url        = fifo_queue.create_fifo()

        assert fifo_queue.message_group_id                    == message_group_id
        assert self.sqs.queue_url(queue_name=temp_queue_name) == queue_url
        assert self.sqs.queue_exists(queue_url=queue_url)     is True
        assert fifo_queue.fifo()                              is True
        assert fifo_queue.info().get('FifoQueue')             == 'true'

        messages = ['1st message', '2nd message', '3rd message']
        for message in messages:
            fifo_queue.push(message)

        assert fifo_queue.messages_in_queue() == 3

        assert fifo_queue.pop() == messages[0]
        assert fifo_queue.pop() == messages[1]
        assert fifo_queue.pop() == messages[2]

        assert self.sqs.queue_delete(queue_url=queue_url) is True

    def test_queue_info(self):
        result = self.sqs.queue_info(queue_url=self.queue_url)
        assert list_set(result) == [ 'ApproximateNumberOfMessages', 'ApproximateNumberOfMessagesDelayed', 'ApproximateNumberOfMessagesNotVisible',
                                     'CreatedTimestamp', 'DelaySeconds', 'LastModifiedTimestamp', 'MaximumMessageSize', 'MessageRetentionPeriod',
                                     'Policy', 'QueueArn', 'QueueName', 'QueueUrl', 'ReceiveMessageWaitTimeSeconds', 'VisibilityTimeout']


    def test_queues(self):
        result = self.sqs.queues()
        pprint(result)

    def test_queue_url_from_queue_arn(self):
        queues_arns = self.sqs.queues_arns()
        if (len(queues_arns)) > 0:
            queue_arn = queues_arns.pop()
            queue_url = self.sqs.queue_url_from_queue_arn(queue_arn=queue_arn)
            assert queue_arn == self.sqs.queue_info(queue_url=queue_url).get('QueueArn')

    @pytest.mark.skip("same problem as .sqs.queues_urls")
    def test_queues(self):
        pprint(self.queue_url)
        result = self.sqs.queues_urls()
        pprint(result)
        result = self.sqs.queues()
        pprint(result)

    # todo find solution for .sqs.queues_urls() delays (for example multiple test executions will show queues that have been deleted
    @pytest.mark.skip("Find solution for the issue caused by .sqs.queues_urls() not having the temp queue created during this test's setUpClass  ")
    def test_queues_urls(self):
        result = self.sqs.queues_urls()
        assert self.queue_url in result

    def test_permission_add(self):
        pprint(self.qeueu)

    @aws_inject('account_id,region')
    def test_permission_add(self, account_id, region):
        label           = 'the-permission-id'
        aws_account_ids = [account_id]
        actions         = ['SendMessage']
        assert self.queue.policy() == {}
        self.queue.permission_add(label=label, aws_account_ids=aws_account_ids, actions=actions)
        assert self.queue.permissions() == [ { 'Action'   : f'SQS:{actions[0]}',
                                               'Effect'   : 'Allow',
                                               'Principal': {'AWS': f'arn:aws:iam::{account_id}:root'},
                                               'Resource' : f'arn:aws:sqs:{region}:{account_id}:{self.queue_name}',
                                               'Sid'      : label}]
        #pprint(self.queue.policy())
        self.queue.permission_delete(label=label)
        assert self.queue.permissions() == []


    def test_permission_add_for_service(self):
        queue_url           = self.queue_url
        action              = 'sqs:SendMessage'
        source_arn          = 'AAAAA'
        effect              = 'Allow'
        service             = 'events.amazonaws.com'
        resource            = "an_resource"
        result = self.sqs.permission_add_for_service(queue_url=queue_url, action=action, source_arn=source_arn, effect=effect, service=service, resource=resource)

        assert result ==  { 'Statement': [ { 'Action'   : 'sqs:SendMessage'                            ,
                                             'Condition': {'ArnEquals': {'aws:SourceArn': source_arn }},
                                             'Effect'   : effect                                       ,
                                             'Principal': {'Service': service                         },
                                             'Resource' : resource                                     ,
                                             'Sid'      : f'sqs:SendMessage-rule-{source_arn}'       }],
                            'Version': '2008-10-17'}


    # def test__delete_temp_queues(self):
    #     for queue in self.sqs.queues():
    #         if queue.get('QueueName').startswith('k8_unit_tests_'):
    #             queue_url = queue.get('QueueUrl')
    #             print(self.sqs.queue_delete(queue_url=queue_url))