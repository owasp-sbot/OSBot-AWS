from unittest import TestCase

from osbot_aws.helpers.SQS_Queue import SQS_Queue
from osbot_utils.utils.Misc import random_string

from osbot_aws.apis.SQS import SQS


class test_SQS(TestCase):

    queue = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.queue_name  = random_string(prefix='unit_tests_temp_queue-')
        cls.queue       = Queue(cls.queue_name).create()
        assert cls.queue.exists() is True

    @classmethod
    def tearDownClass(cls) -> None:
        assert cls.queue.delete() is True

    def setUp(self) -> None:
        self.sqs = SQS()