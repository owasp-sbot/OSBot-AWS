import pytest

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import random_string

from osbot_aws.decorators.aws_inject import aws_inject
from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.test_helpers.Temp_SQS_Queue  import Temp_SQS_Queue


class test_Temp_SQS_Queue(Test_Helper):

    def setUp(self):
        super().setUp()

    @aws_inject('region,account_id')
    def test_simple_execution(self, region, account_id):
        event_data = {'answer': 42}
        queue_name = random_string(prefix="osbot_unit_test")
        with Temp_SQS_Queue(queue_name=queue_name) as queue:
            assert queue_name     == queue.queue_name
            assert queue.exists() is True
            assert queue.queue_url == f'https://{region}.queue.amazonaws.com/{account_id}/{queue.queue_name}'

            assert queue.push(event_data).pop() == event_data
            pprint(queue.info())

    def test_fifo_queue(self):
        message = 'an message'
        with Temp_SQS_Queue(fifo=True) as queue:
            assert queue.fifo()              is True
            assert queue.push(message).pop() == message

