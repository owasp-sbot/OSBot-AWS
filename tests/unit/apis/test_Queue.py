import unittest
from time import sleep
from unittest import TestCase

from pbx_gs_python_utils.utils.Dev import Dev
from pbx_gs_python_utils.utils.Misc import Misc

from osbot_aws.apis.Queue import Queue


class test_Queue(TestCase):

    queue_name = 'unit_tests_temp_queue'
    #queue_name = Misc.random_string_and_numbers('unit_tests_temp_queue_')

    @classmethod
    def setUpClass(cls):
        queue = Queue(test_Queue.queue_name)
        queue.get_n_message(10)  # clean up queue
        #queue.create({})

    @classmethod
    def tearDownClass(cls):
        queue = Queue(test_Queue.queue_name)
        pass

    def setUp(self):
        self.queue = Queue(test_Queue.queue_name)

    def test__init__(self):
        assert type(self.queue).__name__       == 'Queue'
        assert type(self.queue.sqs()).__name__ == 'SQS'

    def test_attributes(self):
        assert  set(self.queue.attributes())  == { 'ApproximateNumberOfMessages', 'ApproximateNumberOfMessagesDelayed',
                                                   'ApproximateNumberOfMessagesNotVisible', 'CreatedTimestamp','DelaySeconds',
                                                   'LastModifiedTimestamp', 'MaximumMessageSize','MessageRetentionPeriod',
                                                   'QueueArn', 'ReceiveMessageWaitTimeSeconds','VisibilityTimeout'}

    def test_create(self):
        assert self.queue.create({}) == self.queue.url()

    def test_list(self):
        assert len(self.queue.list()) > 0

    def test_message_send(self):
        message_1 = Misc.random_string_and_numbers(prefix='Hello_')
        message_2 = Misc.random_string_and_numbers(prefix='World_')
        self.queue.message_send(message_1)                        \
                  .message_send(message_2)
        messages = [self.queue.get_message(),self.queue.get_message()]
        assert message_1 in messages
        assert message_2 in messages
        assert self.queue.get_message() is None



    # Skipped test (created during development, move to separate class)
    @unittest.skip('The most relevant part of this test is shown in the console, and the values are not deterministic')
    def test_prove_that_ApproximateNumberOfMessages_is_Approximate(self):
        self.queue.get_n_message(10)
        message_1 = Misc.random_string_and_numbers(prefix='Hello_')
        message_2 = Misc.random_string_and_numbers(prefix='World 42_')

        assert self.queue.messages_in_queue()    == 0
        assert self.queue.messages_not_visible() == 0
        print()
                                                                                # results           | Accuracy
        print('in queue    : {0}'.format(self.queue.messages_in_queue()))       # 0                 | Correct
        print('..adding two messages')
        self.queue.add(message_1).add(message_2)
        print('in queue    : {0}'.format(self.queue.messages_in_queue() ))      # 0                 | Should be 2
        print('next message: {0}'.format(self.queue.get_message()       ))      # Hello_8PK288      | Correct
        print('in queue    : {0}'.format(self.queue.messages_in_queue() ))      # 0                 | Should be 1
        print('sleep 0.1'                                    ); sleep(0.1)
        print('in queue    : {0}'.format(self.queue.messages_in_queue() ))      # 2                 | Should be 1
        print('sleep 0.1'                                    ); sleep(0.1)
        print('in queue    : {0}'.format(self.queue.messages_in_queue() ))      # 0                 | Should be 1
        print('next message: {0}'.format(self.queue.get_message()       ))      # World 42_O8LIG7   | Correct
        print('in queue    : {0}'.format(self.queue.messages_in_queue() ))      # 0                 | Correct
        print('in queue    : {0}'.format(self.queue.messages_in_queue() ))      # 1                 | Should be 0
        print('next message: {0}'.format(self.queue.get_message()       ))      # None              | Correct
        print('in queue    : {0}'.format(self.queue.messages_in_queue() ))      # 1                 | Should be 0
        print('sleep 0.1'                                    ); sleep(0.1)
        print('in queue    : {0}'.format(self.queue.messages_in_queue() ))      # 1                 | Should be 0
        print('sleep 0.5'                                    ); sleep(0.5)
        print('in queue    : {0}'.format(self.queue.messages_in_queue() ))      # 1                 | Should be 0
        print('sleep 0.5'                                    ); sleep(0.5)
        print('in queue    : {0}'.format(self.queue.messages_in_queue() ))      # 0                 | Should be 0




