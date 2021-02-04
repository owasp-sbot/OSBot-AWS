from osbot_utils.utils.Json import json_loads

from osbot_utils.utils.Misc import random_string

from osbot_utils.utils import Misc

from osbot_aws.decorators.aws_inject import aws_inject
from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_aws.helpers.SQS_Queue import SQS_Queue


class test_SQS_Queue(Test_Helper):

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

    def setUp(self):
        super().setUp()

    @aws_inject('account_id,region')
    def test_attributes(self, account_id, region):
        attributes  = self.queue.attributes()
        assert attributes.get('QueueArn') == f'arn:aws:sqs:{region}:{account_id}:{self.queue_name}'
        assert self.queue.url() in self.queue.sqs().queues_urls()


    def test_message_send(self):
        message_1 = Misc.random_string_and_numbers(prefix='Hello_')
        message_2 = Misc.random_string_and_numbers(prefix='World_')
        self.queue.add(message_1).add(message_2)
        messages = [self.queue.get_message(),self.queue.get_message()]
        assert message_1 in messages
        assert message_2 in messages
        assert self.queue.get_message() is None

    def test_get_message_with_attributes(self):
        body = 'this is the body of the message.... 132'
        attributes = {'var_1': 'value_1', 'var_2': 'value_2'}

        self.queue.message_send(body,attributes)
        data = self.queue.get_message_with_attributes()
        assert body       == data[0]
        assert attributes == data[1]
        assert attributes.get('var_1') == 'value_1'

    def test_push_pull(self):
        self.queue.push( {'var_1': 'value_1' , 'var_2': 'value_2'})
        assert json_loads(self.queue.get_message()) == {"var_1": "value_1", "var_2": "value_2"}

        self.queue.push({'var_3': 'value_3', 'var_4': 'value_4'})
        assert self.queue.pull() == {'var_3': 'value_3' , 'var_4': 'value_4'}               # is python object

        self.queue.push([{'var_5': 'value_5'}, {'var_6': 'value_7'}])                       # push an array
        assert self.queue.pull() == [{'var_5': 'value_5'}, {'var_6': 'value_7'}]            # comes back as an array

    @aws_inject('account_id,region')
    def test_permissions(self, account_id, region):
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
        self.queue.permission_delete(label=label)
        assert self.queue.permissions() == []


    # # Skipped test (created during development, move to separate class)
    # @unittest.skip('The most relevant part of this test is shown in the console, and the values are not deterministic')
    # def _test_prove_that_ApproximateNumberOfMessages_is_Approximate(self):
    #     self.queue.get_n_message(10)
    #     message_1 = Misc.random_string_and_numbers(prefix='Hello_')
    #     message_2 = Misc.random_string_and_numbers(prefix='World 42_')
    #
    #     assert self.queue.messages_in_queue()    == 0
    #     assert self.queue.messages_not_visible() == 0
    #     print()
    #                                                                             # results           | Accuracy
    #     print('in queue    : {0}'.format(self.queue.messages_in_queue()))       # 0                 | Correct
    #     print('..adding two messages')
    #     self.queue.add(message_1).add(message_2)
    #     print('in queue    : {0}'.format(self.queue.messages_in_queue() ))      # 0                 | Should be 2
    #     print('next message: {0}'.format(self.queue.get_message()       ))      # Hello_8PK288      | Correct
    #     print('in queue    : {0}'.format(self.queue.messages_in_queue() ))      # 0                 | Should be 1
    #     print('sleep 0.1'                                    ); sleep(0.1)
    #     print('in queue    : {0}'.format(self.queue.messages_in_queue() ))      # 2                 | Should be 1
    #     print('sleep 0.1'                                    ); sleep(0.1)
    #     print('in queue    : {0}'.format(self.queue.messages_in_queue() ))      # 0                 | Should be 1
    #     print('next message: {0}'.format(self.queue.get_message()       ))      # World 42_O8LIG7   | Correct
    #     print('in queue    : {0}'.format(self.queue.messages_in_queue() ))      # 0                 | Correct
    #     print('in queue    : {0}'.format(self.queue.messages_in_queue() ))      # 1                 | Should be 0
    #     print('next message: {0}'.format(self.queue.get_message()       ))      # None              | Correct
    #     print('in queue    : {0}'.format(self.queue.messages_in_queue() ))      # 1                 | Should be 0
    #     print('sleep 0.1'                                    ); sleep(0.1)
    #     print('in queue    : {0}'.format(self.queue.messages_in_queue() ))      # 1                 | Should be 0
    #     print('sleep 0.5'                                    ); sleep(0.5)
    #     print('in queue    : {0}'.format(self.queue.messages_in_queue() ))      # 1                 | Should be 0
    #     print('sleep 0.5'                                    ); sleep(0.5)
    #     print('in queue    : {0}'.format(self.queue.messages_in_queue() ))      # 0                 | Should be 0
    #



