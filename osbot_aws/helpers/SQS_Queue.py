import json

from osbot_utils.utils.Json import json_dumps, json_loads

from osbot_aws.apis.SQS import SQS
from osbot_utils.decorators.methods.cache import cache
from osbot_utils.decorators.methods.catch import catch

from osbot_aws.apis.IAM import IAM

from osbot_aws.apis.Lambda import Lambda
from osbot_aws.apis.Session import Session
from osbot_utils.utils import Misc

class SQS_Queue:                                        # todo refactor main methods to SSM class
    def __init__(self, queue_name=None, url=None):
        self._url          = url
        self.queue_name    = queue_name
        self.queue_url     = None
        self.lambda_policy = 'arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole'

    @cache
    def sqs(self):
        return SQS()

    # main methods

    def add(self, body, attributes=None):
        self.message_send(body,attributes)
        return self

    def arn(self):
        return self.attributes().get('QueueArn')

    def attributes(self, attribute_names='All'):
        return self.sqs().queue_attributes(queue_url=self.url(),attribute_names=attribute_names)

    def attributes_update(self, new_attributes):
        return self.sqs().queue_attributes_update(queue_url=self.url(), new_attributes=new_attributes)

    def create(self,attributes=None):
        return self.sqs().queue_create(queue_name=self.queue_name, attributes=attributes)

    def delete(self):
        return self.sqs().queue_delete(queue_url=self.url())

    def exists(self):
        return self.sqs().queue_exists(queue_url=self.url())

    def get_message(self, delete_message=True):
        return self.sqs().queue_message_get(queue_url=self.url(), delete_message=delete_message)

    def get_message_with_attributes(self, delete_message=True):
        return self.sqs().queue_message_get_with_attributes(queue_url=self.url(), delete_message=delete_message)

    def get_n_message(self, n, delete_message=True):
        return self.sqs().queue_messages_get_n(queue_url=self.url(), n=n, delete_message=delete_message)

    def info(self):                         # consistent method with similar classes like Lambda
        return self.sqs().info()

    def message_raw(self):
        return self.sqs().queue_message_get_raw(queue_url=self.url())

    def message_delete(self, receipt_handle):
        return self.sqs().queue_message_delete(queue_url=self.url(), receipt_handle=receipt_handle)

    def message_send(self,body,attributes_data=None):
        return self.sqs().queue_message_send(queue_url=self.url(), body=body, attributes_data=attributes_data)

    def messages_in_queue(self):
        return self.sqs().queue_messages_count(queue_url=self.url())

    def messages_not_visible(self):
        return self.sqs().queue_messages_count_not_visible(queue_url=self.url())

    def permission_add(self, label, aws_account_ids, actions):
        return self.sqs().permission_add(queue_url=self.url(), label=label, aws_account_ids=aws_account_ids, actions=actions)

    def permission_delete(self, label):
        return self.sqs().permission_delete(queue_url=self.url(), label=label)

    def permissions(self):
        return self.sqs().permissions(queue_url=self.url())

    def policy(self):
        return self.sqs().policy(queue_url=self.url())

    def push(self, data):
        if data:
            self.message_send(json_dumps(data))
        return self

    def pull(self, delete_message=True):
        data_json = self.get_message(delete_message=delete_message)
        if data_json:
            return json_loads(data_json)
        return None

    @cache
    def url(self):
        return self.sqs().queue_url(queue_name=self.queue_name)
