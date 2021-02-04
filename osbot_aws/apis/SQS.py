from osbot_utils.utils.Json import json_loads

from osbot_utils.utils.Misc import array_pop, array_get

from osbot_utils.decorators.methods.catch import catch
from osbot_utils.decorators.methods.cache import cache

from osbot_aws.apis.Session import Session


class SQS:

    @cache
    def client(self):
        return Session().client('sqs')

    @catch
    def queue_attributes(self, queue_url, attribute_names='All'):
        return self.client().get_queue_attributes(QueueUrl=queue_url, AttributeNames=[attribute_names]).get('Attributes')

    def queue_attributes_update(self, queue_url, new_attributes):
        return self.client().set_queue_attributes(QueueUrl=queue_url, Attributes=new_attributes)

    def queue_create(self, queue_name, attributes=None):
        kwargs = { "QueueName": queue_name,
                   "Attributes": attributes or {} }
        return self.client().create_queue(**kwargs).get('QueueUrl')

    def queue_delete(self, queue_url):
        if self.queue_exists(queue_url=queue_url) is False: return False
        self.client().delete_queue(QueueUrl=queue_url)
        return self.queue_exists(queue_url=queue_url) is False

    def queue_exists(self, queue_url):
        return self.queue_info(queue_url=queue_url).get('error') is None

    def queue_info(self, queue_url):                         # consistent method with similar classes like Lambda
        return self.queue_attributes(queue_url=queue_url)

    def queue_message_delete(self, queue_url, receipt_handle):
        return self.client().delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)

    def queue_message_get(self, queue_url, delete_message=True):
        message = self.queue_message_get_raw(queue_url)
        if message:
            body = message.get('Body')
            receipt_handle = message.get('ReceiptHandle')
            if delete_message:
                self.queue_message_delete(queue_url, receipt_handle)
            return body

    def queue_message_get_raw(self, queue_url, message_attribute_names=None):
        kwargs = {"QueueUrl"             : queue_url,
                  "MessageAttributeNames": message_attribute_names or ['All'],
                  "MaxNumberOfMessages"  : 1 }
        messages = self.client().receive_message(**kwargs).get('Messages')
        return array_get(messages,0)                        # there will only be a max of one message in queue

    def queue_message_get_with_attributes(self, queue_url, delete_message=True):
        message = self.queue_message_get_raw(queue_url=queue_url)
        if message:
            body            = message.get('Body')
            attributes      = message.get('MessageAttributes')
            receipt_handle  = message.get('ReceiptHandle')
            attributes_data = {}
            if attributes:
                for key,value in attributes.items():
                    attributes_data[key] = value.get('StringValue')
            if delete_message:
                self.queue_message_delete(queue_url=queue_url,receipt_handle=receipt_handle)
            return body, attributes_data

    def queue_messages_get_n(self, queue_url, n, delete_message=True):      # todo see if we can use client().receive_message with a higher value of MaxNumberOfMessages
        messages = []
        for i in range(0,n):
            message = self.queue_message_get(queue_url=queue_url, delete_message=delete_message)
            if message:
                messages.append(message)
            else:
                break
        return messages

    def queue_message_send(self,queue_url, body,attributes_data=None):
        if attributes_data is None:
            return self.client().send_message(QueueUrl=queue_url, MessageBody=body).get('MessageId')
        else:
            attributes = {}
            for key,value in attributes_data.items():
                attributes[key] = { 'StringValue': value , 'DataType': 'String'}
            return self.client().send_message(QueueUrl=queue_url,MessageBody=body, MessageAttributes=attributes).get('MessageId')

    def queue_messages_count(self, queue_url):
        return int(self.queue_attributes(queue_url=queue_url).get('ApproximateNumberOfMessages'))

    def queue_messages_count_not_visible(self, queue_url):
        return int(self.queue_attributes(queue_url=queue_url).get('ApproximateNumberOfMessagesNotVisible'))

    def queue_url(self, queue_name):
        return self.client().get_queue_url(QueueName=queue_name).get('QueueUrl')

    def queues_urls(self):
        return self.client().list_queues().get('QueueUrls')

    @catch
    def permission_add(self, queue_url, label, aws_account_ids, actions):
        self.permission_delete(queue_url, label)  # delete if already exists
        params = {'QueueUrl': queue_url,
                  'Label': label,
                  'AWSAccountIds': aws_account_ids,
                  'Actions': actions}
        return self.client().add_permission(**params)

    @catch
    def permission_delete(self, queue_url, label):
        params = {  'QueueUrl'     : queue_url      ,
                    'Label'        : label          ,}
        return self.client().remove_permission(**params)

    def permissions(self, queue_url):
        return self.policy(queue_url).get('Statement', [])

    def policy(self, queue_url):
        value = self.queue_attributes(queue_url=queue_url).get('Policy')
        if value:
            return json_loads(value)
        return {}



    # todo refactor methods bellow into an Lambda Helper class (there are a couple unit tests that need this)
    # def policy_add_sqs_permissions_to_lambda_role(self, lambda_name):
    #     aws_lambda    = Lambda(lambda_name)
    #     iam_role_name = aws_lambda.configuration().get('Role').split(':role/').pop()
    #     IAM(role_name=iam_role_name).role_policy_attach(self.lambda_policy)
    #     return iam_role_name
    #
    # def policy_remove_sqs_permissions_to_lambda_role(self, lambda_name):
    #     aws_lambda    = Lambda(lambda_name)
    #     iam_role_name = aws_lambda.configuration().get('Role').split(':role/').pop()
    #     IAM(role_name=iam_role_name).role_policy_detach(self.lambda_policy)
    #     return iam_role_name
