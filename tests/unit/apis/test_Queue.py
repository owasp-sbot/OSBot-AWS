from pbx_gs_python_utils.utils.Misc         import Misc
from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.Queue                   import Queue
from osbot_aws.apis.test_helpers.Temp_Queue import Temp_Queue
from osbot_utils.decorators.Method_Wrappers      import aws_inject

class test_Queue(Test_Helper):

    def setUp(self):
        super().setUp()

    def test_attributes_create__exists__list(self):
        assert Queue().exists() is False
        with Temp_Queue() as temp_Queue:
            assert 'QueueArn'                in set(temp_Queue.queue.attributes())
            assert 'unit_tests_temp_queue_'  in temp_Queue.queue_name
            assert temp_Queue.queue.exists() is True
            assert len(Queue().list()) > 0
            self.result = temp_Queue.queue.attributes()

    def test_message_send(self):
        with Temp_Queue() as temp_Queue:
            queue = temp_Queue.queue
            message_1 = Misc.random_string_and_numbers(prefix='Hello_')
            message_2 = Misc.random_string_and_numbers(prefix='World_')
            queue.add(message_1).add(message_2)
            messages = [queue.get_message(),queue.get_message()]
            assert message_1 in messages
            assert message_2 in messages
            assert queue.get_message() is None

    def test_get_message_with_attributes(self):
        with Temp_Queue() as temp_Queue:
            queue = temp_Queue.queue
            body = 'this is the body of the message.... 132'
            attributes = {'var_1': 'value_1', 'var_2': 'value_2'}

            queue.message_send(body,attributes)
            data = queue.get_message_with_attributes()
            assert body       == data[0]
            assert attributes == data[1]
            assert attributes.get('var_1') == 'value_1'

    def test_push_pull(self):
        with Temp_Queue() as temp_Queue:
            queue = temp_Queue.queue
            queue.push( {'var_1': 'value_1' , 'var_2': 'value_2'})
            assert queue.get_message() == '{"var_1": "value_1", "var_2": "value_2"}'       # is json string

            queue.push({'var_3': 'value_3', 'var_4': 'value_4'})
            assert queue.pull() == {'var_3': 'value_3' , 'var_4': 'value_4'}              # is python object

            queue.push([{'var_5': 'value_5'}, {'var_6': 'value_7'}])                       # push an array
            assert queue.pull() == [{'var_5': 'value_5'}, {'var_6': 'value_7'}]            # comes back as an array

    @aws_inject('account_id')
    def test_permissions(self, account_id):
        with Temp_Queue() as temp_Queue:
            queue       = temp_Queue.queue
            queue_name  = temp_Queue.queue_name
            queue_url   = queue.url()
            label       = 'the-permission-id'
            account_ids = [account_id]
            actions     = ['SendMessage']
            assert queue.policy() == {}
            queue.permission_add(queue_url,label, account_ids, actions)
            assert queue.permissions() == [ { 'Action'   : f'SQS:{actions[0]}',
                                              'Effect'   : 'Allow',
                                              'Principal': {'AWS': f'arn:aws:iam::{account_id}:root'},
                                              'Resource' : f'arn:aws:sqs:eu-west-1:{account_id}:{queue_name}',
                                              'Sid'      : label}]
            queue.permission_delete(queue_url, label)
            assert queue.permissions() == []


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



