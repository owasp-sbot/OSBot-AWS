from osbot_utils.utils.Lists import array_get

from osbot_utils.decorators.lists.index_by import index_by
from osbot_utils.decorators.methods.cache_on_self import cache_on_self

from osbot_utils.utils.Json import json_loads, json_to_str

from osbot_utils.utils.Misc import list_set

from osbot_utils.decorators.methods.catch import catch
from osbot_utils.decorators.methods.cache import cache

from osbot_aws.apis.Session import Session


class SQS:

    @cache_on_self
    def client(self):
        return Session().client('sqs')

    @catch
    def queue_attributes(self, queue_url, attribute_names='All'):
        queue_data = self.client().get_queue_attributes(QueueUrl=queue_url, AttributeNames=[attribute_names]).get('Attributes')
        queue_data['QueueUrl' ] = queue_url                              # add this important value (which is missing from the current data returned from AWS)
        queue_data['QueueName'] = queue_data['QueueUrl' ].split('/').pop()
        return queue_data

    def queue_attributes_update(self, queue_url, new_attributes):
        return self.client().set_queue_attributes(QueueUrl=queue_url, Attributes=new_attributes)

    def queue_create(self, queue_name, attributes=None):
        kwargs = { "QueueName": queue_name,
                   "Attributes": attributes or {} }
        return self.client().create_queue(**kwargs).get('QueueUrl')

    def queue_create_fifo(self, queue_name, attributes=None):
        if attributes is None:
            attributes = {}
        attributes.update({'FifoQueue'                : 'True'  ,
                           'ContentBasedDeduplication': 'True' })

        return self.queue_create(queue_name=queue_name, attributes=attributes)

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

    def queue_messages_get_n(self, queue_url, n=1, delete_message=True):      # todo see if we can use client().receive_message with a higher value of MaxNumberOfMessages
        messages = []
        for i in range(0,n):
            message = self.queue_message_get(queue_url=queue_url, delete_message=delete_message)
            if message:
                messages.append(message)
            else:
                break
        return messages

    def queue_message_send(self, queue_url, body, message_group_id=None, attributes_data=None):
        kwargs = {"QueueUrl"         : queue_url,
                  "MessageBody"      : body     ,
                  "MessageAttributes": {}}

        if attributes_data:
            for key,value in attributes_data.items():
                kwargs['MessageAttributes'][key] = { 'StringValue': value , 'DataType': 'String'}
        if message_group_id:
            kwargs["MessageGroupId"] = message_group_id

        return self.client().send_message(**kwargs).get('MessageId')

    def queue_message_send_fifo(self, queue_url, message_group_id, body, attributes_data=None):
        return self.queue_message_send(queue_url=queue_url, message_group_id=message_group_id, body=body, attributes_data=attributes_data)

    def queue_messages_count(self, queue_url):
        return int(self.queue_attributes(queue_url=queue_url).get('ApproximateNumberOfMessages'))

    def queue_messages_count_not_visible(self, queue_url):
        return int(self.queue_attributes(queue_url=queue_url).get('ApproximateNumberOfMessagesNotVisible'))

    def queue_url(self, queue_name):
        return self.client().get_queue_url(QueueName=queue_name).get('QueueUrl')

    def queue_url_from_queue_arn(self, queue_arn):
        result = self.queues(index_by='QueueArn')
        return result.get(queue_arn, {}).get('QueueUrl')

    @index_by
    def queues(self):                               # todo: see if there is a better way to get this info about existing queues
        """Note: there could be missing entries since the list of queues doesn't update as fast as it should
                 (i.e. SQS.queues_urls(): might have more entries that SQS.queues() )
        """
        data = []
        for queue_url in self.queues_urls():
            queue_info = self.queue_info(queue_url=queue_url)
            if queue_info.get('error') is None:
                data.append(queue_info)
        return data

    def queues_arns(self):
        return list_set(self.queues(index_by="QueueArn"))

    def queues_urls(self):
        return self.client().list_queues().get('QueueUrls')

    @catch
    def permission_add(self, queue_url, label, aws_account_ids, actions):
        self.permission_delete(queue_url, label)  # delete if already exists
        params = {'QueueUrl'     : queue_url       ,
                  'Label'        : label           ,
                  'AWSAccountIds': aws_account_ids ,
                  'Actions'      : actions         }
        return self.client().add_permission(**params)

    # todo: see if there is a better way to do this. It shouldn't be needed to write this method, but boto3's add_permission doesn't seem to have the ability to control the Condition and Pricipal values
    def permission_add_for_service(self, queue_url, source_arn, service, resource, action='sqs:SendMessage', effect='Allow'):
        policy_statement_id = f'{action}-rule-{source_arn}'
        statement  = { 'Action'   : action,
                       'Condition': {'ArnEquals': {'aws:SourceArn':source_arn}},
                       'Effect'   : effect,
                       'Principal': {'Service': service},
                       'Resource' : resource,
                       'Sid'      : policy_statement_id }

        policy = self.policy(queue_url=queue_url)
        if policy == {}:
            policy = {'Statement' : []           ,
                      'Version'   : '2008-10-17' }
        policy.get('Statement').append(statement)
        policy_str = json_to_str(policy)
        self.queue_attributes_update(queue_url=queue_url, new_attributes={"Policy": policy_str})
        return self.policy(queue_url=queue_url)


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
