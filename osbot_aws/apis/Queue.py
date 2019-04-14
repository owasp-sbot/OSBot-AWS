from pbx_gs_python_utils.utils.Misc import Misc

from osbot_aws.apis.Session import Session


class Queue:
    def __init__(self, queue_name):
        self._url       = None
        self._sqs       = None
        self.queue_name = queue_name

        # duplicate methods
        self.add        = self.message_send

    # helper methods
    def sqs(self):
        if self._sqs is None:
            self._sqs = Session().client('sqs')
        return self._sqs

    def url(self):
        if self._url is None:
            self._url =  self.sqs().get_queue_url(QueueName=self.queue_name).get('QueueUrl')
        return self._url


    # main methods
    def attributes(self):
        return self.sqs().get_queue_attributes(QueueUrl=self.url(),AttributeNames=['All']).get('Attributes')

    def attributes_update(self, new_attributes):
        return self.sqs().set_queue_attributes(QueueUrl=self.url(), Attributes=new_attributes)


    def create(self,attributes):
       return self.sqs().create_queue(QueueName=self.queue_name,Attributes=attributes).get('QueueUrl')

    def get_message(self, delete_message=True):
        message = self.message_raw()
        if message:
            body = message.get('Body')
            receipt_handle = message.get('ReceiptHandle')
            if delete_message:
                self.message_delete(receipt_handle)
            return body

    def get_n_message(self, n, delete_message=True):
        messages = []
        for i in range(0,n):
            message = self.get_message(delete_message)
            if message:
                messages.append(message)
            else:
                break
        return messages

    def list(self):
        return self.sqs().list_queues().get('QueueUrls')


    def message_raw(self):
        messages = self.sqs().receive_message(QueueUrl=self.url()).get('Messages')
        return Misc.array_pop(messages,0)

    def message_delete(self, receipt_handle):
        return self.sqs().delete_message(QueueUrl=self.url(), ReceiptHandle=receipt_handle)


    #def add(self, message, attributes=None): return self.message_send(message,attributes)

    def message_send(self,message,attributes=None):
        self.sqs().send_message(QueueUrl=self.url(),MessageBody=message).get('MessageId')
        return self

    def messages_in_queue(self):
        return int(self.attributes().get('ApproximateNumberOfMessages'))

    def messages_not_visible(self):
        return int(self.attributes().get('ApproximateNumberOfMessagesNotVisible'))