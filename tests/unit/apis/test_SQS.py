from unittest import TestCase

from osbot_aws.helpers.SQS_Queue import SQS_Queue
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import random_string

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
