import json

from osbot_aws.apis.IAM import IAM
from pbx_gs_python_utils.utils.Misc import Misc

from osbot_aws.apis.Lambda import Lambda
from osbot_aws.apis.Session import Session
from osbot_utils.decorators.Method_Wrappers import cache, catch


class Queue:
    def __init__(self, queue_name=None, url=None):
        self._url          = url
        self._sqs          = None
        self.queue_name    = queue_name
        self.queue_url     = None
        self.lambda_policy = 'arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole'

    # helper methods
    @cache
    def sqs(self):
        return  Session().client('sqs')

    # main methods

    def add(self, body, attributes=None):
        self.message_send(body,attributes)
        return self

    def arn(self):
        return self.attributes().get('QueueArn')

    @catch
    def attributes(self, attribute_names='All'):
        return self.sqs().get_queue_attributes(QueueUrl=self.url(),AttributeNames=[attribute_names]).get('Attributes')

    def attributes_update(self, new_attributes):
        return self.sqs().set_queue_attributes(QueueUrl=self.url(), Attributes=new_attributes)

    def create_raw(self,attributes=None):
        if attributes is None: attributes = {}
        return self.sqs().create_queue(QueueName=self.queue_name,Attributes=attributes).get('QueueUrl')

    def create(self,attributes=None):
        self.queue_url = self.create_raw(attributes)
        if self.queue_url:
            return self
        return None

    def delete(self):
        if self.exists() is False: return False
        self.sqs().delete_queue(QueueUrl=self.url())
        return self.exists() is False

    def exists(self):
        return self.attributes().get('error') is None

    def get_message(self, delete_message=True):
        message = self.message_raw()
        if message:
            body = message.get('Body')
            receipt_handle = message.get('ReceiptHandle')
            if delete_message:
                self.message_delete(receipt_handle)
            return body

    def get_message_with_attributes(self, delete_message=True):
        message = self.message_raw()
        if message:
            body            = message.get('Body')
            attributes      = message.get('MessageAttributes')
            receipt_handle  = message.get('ReceiptHandle')
            attributes_data = {}
            if attributes:
                for key,value in attributes.items():
                    attributes_data[key] = value.get('StringValue')
            if delete_message:
                self.message_delete(receipt_handle)
            return body, attributes_data

    def get_n_message(self, n, delete_message=True):
        messages = []
        for i in range(0,n):
            message = self.get_message(delete_message)
            if message:
                messages.append(message)
            else:
                break
        return messages

    def info(self):                         # consistent method with similar classes like Lambda
        return self.attributes()

    def list(self):
        return self.sqs().list_queues().get('QueueUrls')

    def message_raw(self):
        messages = self.sqs().receive_message(QueueUrl=self.url(), MessageAttributeNames=['All']).get('Messages')
        return Misc.array_pop(messages,0)

    def message_delete(self, receipt_handle):
        return self.sqs().delete_message(QueueUrl=self.url(), ReceiptHandle=receipt_handle)

    def message_send(self,body,attributes_data=None):
        if attributes_data is None:
            return self.sqs().send_message(QueueUrl=self.url(), MessageBody=body).get('MessageId')
        else:
            attributes = {}
            for key,value in attributes_data.items():
                attributes[key] = { 'StringValue': value , 'DataType': 'String'}
            return self.sqs().send_message(QueueUrl=self.url(),MessageBody=body, MessageAttributes=attributes).get('MessageId')

    def messages_in_queue(self):
        return int(self.attributes().get('ApproximateNumberOfMessages'))

    def messages_not_visible(self):
        return int(self.attributes().get('ApproximateNumberOfMessagesNotVisible'))

    @catch
    def permission_add(self, queue_url, label, aws_account_ids, actions):
        self.permission_delete(queue_url,label)                             # delete if already exists
        params = {  'QueueUrl'     : queue_url      ,
                    'Label'        : label          ,
                    'AWSAccountIds': aws_account_ids,
                    'Actions'      : actions      }
        return self.sqs().add_permission(**params)

    @catch
    def permission_delete(self, queue_url, label):
        params = {  'QueueUrl'     : queue_url      ,
                    'Label'        : label          ,}
        return self.sqs().remove_permission(**params)

    def permissions(self):
        return self.policy().get('Statement', [])

    def policy(self):
        value = self.attributes().get('Policy')
        if value:
            return json.loads(value)
        return {}

    def policy_add_sqs_permissions_to_lambda_role(self, lambda_name):
        aws_lambda    = Lambda(lambda_name)
        iam_role_name = aws_lambda.configuration().get('Role').split(':role/').pop()
        IAM(role_name=iam_role_name).role_policy_attach(self.lambda_policy)
        return iam_role_name

    def policy_remove_sqs_permissions_to_lambda_role(self, lambda_name):
        aws_lambda    = Lambda(lambda_name)
        iam_role_name = aws_lambda.configuration().get('Role').split(':role/').pop()
        IAM(role_name=iam_role_name).role_policy_detach(self.lambda_policy)
        return iam_role_name

    def push(self, data):
        if data:
            self.message_send(json.dumps(data))
        return self

    def pull(self, delete_message=True):
        data_json = self.get_message(delete_message=delete_message)
        if data_json:
            return json.loads(data_json)
        return None

    def set_queue_name(self, queue_name):
        self.queue_name = queue_name
        self._url       = None          # need to reset this value or the old value will still be used
        return self

    @cache
    def url(self):
        return self.sqs().get_queue_url(QueueName=self.queue_name).get('QueueUrl')
