from unittest import TestCase

import pytest

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

    def test_create(self):
        temp_queue_name = random_string(prefix='unit_tests_another-temp_queue-')
        queue_url = self.sqs.queue_create(queue_name=temp_queue_name)

        assert queue_url == self.sqs.queue_url(queue_name=temp_queue_name)
        assert self.sqs.queue_exists(queue_url=queue_url) is True
        assert self.sqs.queue_delete(queue_url=queue_url) is True

    def test_queue_info(self):
        result = self.sqs.queue_info(queue_url=self.queue_url)
        assert list_set(result) == [ 'ApproximateNumberOfMessages', 'ApproximateNumberOfMessagesDelayed', 'ApproximateNumberOfMessagesNotVisible',
                                     'CreatedTimestamp', 'DelaySeconds', 'LastModifiedTimestamp', 'MaximumMessageSize', 'MessageRetentionPeriod',
                                     'QueueArn', 'QueueName', 'QueueUrl', 'ReceiveMessageWaitTimeSeconds', 'VisibilityTimeout']


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


class BBB(TestCase):
    def setUp(self) -> None:
        self.sqs = SQS()

    def test_queues_urls(self):
        #pprint(self.queue_url)
        result = self.sqs.queues_urls()
        pprint(result)
    # def test_delete_temp_queues(self):
    #     queues_urls = self.sqs.queues_urls()
    #     for queue_url  in queues_urls:
    #         if "unit_tests" in queue_url:
    #             pprint(self.sqs.queue_delete(queue_url=queue_url))