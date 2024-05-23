from botocore.exceptions import ClientError
from osbot_aws.AWS_Config import AWS_Config
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.utils.Misc import wait_for
from osbot_utils.decorators.methods.remove_return_value import remove_return_value
from osbot_utils.decorators.lists.index_by import index_by

from osbot_aws.apis.Session import Session
from osbot_utils.utils.Status import status_warning, status_ok, status_error

from osbot_aws.aws.sts.STS import STS


class Cloud_Watch_Logs():
    def __init__(self):
        self.aws_config = AWS_Config()
        self.account_id  = self.aws_config.aws_session_account_id()
        self.region_name = self.aws_config.aws_session_region_name()

    @cache_on_self
    def client(self):
        return Session().client('logs')

    @cache_on_self
    def sts(self):
        return STS()

    def destinations(self):
        return self.client().describe_destinations().get('destinations')

    def export_tasks(self):
        return self.client().describe_export_tasks().get('exportTasks')

    def log_events(self, log_group_name, log_stream_name):
        if self.log_stream_exists(log_group_name=log_group_name, log_stream_name=log_stream_name):
            return '\n'.join(self.log_events_messages(log_group_name=log_group_name, log_stream_name=log_stream_name))
        return ''

    def log_events_messages(self, log_group_name, log_stream_name):
        messages = []
        events = self.log_events_raw(log_group_name=log_group_name, log_stream_name=log_stream_name).get('events')
        for event in events:
            messages.append(event.get('message'))
        return messages

    @remove_return_value(field_name='ResponseMetadata')
    def log_events_put(self, log_group_name, log_stream_name, log_events, next_sequence_token=None):
        kwargs = {  'logGroupName' : log_group_name,
                    'logStreamName': log_stream_name,
                    'logEvents'    : log_events }

        if next_sequence_token:
            kwargs.update({'sequenceToken': next_sequence_token})

        result = self.client().put_log_events(**kwargs)
        return result.get('nextSequenceToken')

    @remove_return_value(field_name='ResponseMetadata')
    def log_events_raw(self, log_group_name, log_stream_name):
        result = self.client().get_log_events(logGroupName=log_group_name, logStreamName=log_stream_name)
        return result
        # todo add support for these filters
        # startTime = 123,
        # endTime = 123,
        # nextToken = 'string',
        # limit = 123,
        # startFromHead = True | False

    def log_group(self,log_group_name):
        log_group_arn = self.log_group_arn(log_group_name)
        log_groups    = self.log_groups(log_group_prefix=log_group_name)
        for log_group in log_groups:
            if log_group_arn == log_group.get('arn'):
                return log_group

    def log_group_arn(self, log_group_name):
        return f'arn:aws:logs:{self.region_name}:{self.account_id}:log-group:{log_group_name}:*'

    def log_group_create(self, log_group_name, tags=None):
        if self.log_group_exists(log_group_name):
            return status_warning(f'log group already existed: {log_group_name}')
        kwargs = {'logGroupName' : log_group_name}
        if tags:
            kwargs['tags'] = tags
        self.client().create_log_group(**kwargs)
        return status_ok(message=f"log group created ok: {log_group_name}")

    def log_group_delete(self,log_group_name):
        if self.log_group_exists(log_group_name) is False:
            return status_warning(f'log group did not exist: {log_group_name}')
        self.client().delete_log_group(logGroupName= log_group_name)
        return status_ok(message=f"log group deleted ok: {log_group_name}")

    def log_group_exists(self, log_group_name):
        return self.log_group(log_group_name=log_group_name) is not None

    def log_group_not_exists(self, log_group_name):
        return self.log_group_exists(log_group_name) is False

    @index_by
    def log_groups(self, log_group_prefix=None):
        kwargs = {}
        if log_group_prefix:
            kwargs['logGroupNamePrefix'] = log_group_prefix
        return self.client().describe_log_groups(**kwargs).get('logGroups')     # todo add pagination (see how IAM does it)

    def log_stream_create(self, log_group_name, log_stream_name):
        if self.log_group_not_exists(log_group_name=log_group_name):                    # if the log group doesn't exist, create it
            self.log_group_create(log_group_name).get('status')
        try:
            self.client().create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)
            return status_ok(message=f"log stream created ok: {log_stream_name}")
        except ClientError as exception:
            if exception.response['Error']['Code'] == 'ResourceAlreadyExistsException':
                return status_warning(message=f"log stream already existed: {log_stream_name}")
            return status_error(message=f'exception', error=exception)

    def log_stream(self, log_group_name, log_stream_name):                                      # todo: map out the performance implications of .log_streams(...) using describe_log_streams is it looks like it has very low limits of 5 TPS per account per region
        log_stream_arn = self.log_stream_arn(log_group_name=log_group_name, log_stream_name=log_stream_name)
        log_streams    = self.log_streams   (log_group_name=log_group_name, log_stream_name_prefix=log_stream_name)
        for log_stream in log_streams:
            if log_stream.get('arn') == log_stream_arn:
                return log_stream

    def log_stream_arn(self, log_group_name, log_stream_name):
        return f'arn:aws:logs:{self.region_name}:{self.account_id}:log-group:{log_group_name}:log-stream:{log_stream_name}'

    def log_stream_delete(self,log_group_name, log_stream_name):
        if self.log_stream_exists(log_group_name, log_stream_name) is False:
            return status_warning(f'log stream did not exist: {log_group_name}')
        self.client().delete_log_stream(logGroupName= log_group_name, logStreamName=log_stream_name)
        return status_ok(message=f"log stream deleted ok: {log_stream_name}")

    def log_stream_exists(self, log_group_name, log_stream_name):
        return self.log_stream(log_group_name=log_group_name, log_stream_name=log_stream_name) is not None

    def log_stream_next_token(self,log_group_name, log_stream_name):
        log_stream = self.log_stream(log_group_name=log_group_name, log_stream_name=log_stream_name)
        if log_stream:
            return log_stream.get('nextForwardToken')

    def log_stream_not_exists(self, log_group_name, log_stream_name):
        return self.log_stream_exists(log_group_name=log_group_name, log_stream_name=log_stream_name) is False

    def log_streams(self, log_group_name, log_stream_name_prefix=None):     # todo: map out the performance implications of using describe_log_streams is it looks like it has very low limits of 5 TPS per account per region
        if self.log_group_not_exists(log_group_name=log_group_name):
            return []
        kwargs = {'logGroupName': log_group_name}
        if log_stream_name_prefix:
            kwargs['logStreamNamePrefix'] = log_stream_name_prefix
        result = self.client().describe_log_streams(**kwargs)
        return result.get('logStreams')

    def metric_filters(self):
        return self.client().describe_metric_filters().get('metricFilters')

    def queries(self):
        return self.client().describe_queries().get('queries')

    def query_definitions(self):
        return self.client().describe_query_definitions().get('queryDefinitions')

    def resource_policies(self):
        return self.client().describe_resource_policies().get('resourcePolicies')

    def subscription_filters(self, log_group_name):
        return self.client().describe_subscription_filters(logGroupName=log_group_name).get('subscriptionFilters')

    def wait_for_log_events(self, log_group_name, log_stream_name, max_attempts=20 ,sleep_for=0.1):
        for i in range(0, max_attempts):
            result = self.log_events_raw(log_group_name=log_group_name, log_stream_name=log_stream_name)
            events = result.get('events')
            if len(events) > 0:
                #print(f' got logs after {i} * {sleep_for} seconds')        # note: when coding this this value was between 4 and 8
                return events
            wait_for(sleep_for)
        return []


