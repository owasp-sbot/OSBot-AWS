import boto3

from osbot_aws.apis.STS import STS
from osbot_utils.decorators.lists.index_by import index_by

from osbot_utils.decorators.methods.cache import cache

from osbot_aws.apis.Session import Session
from osbot_utils.utils.Status import status_warning, status_ok, status_error


class Cloud_Watch_Logs():
    def __init__(self):
        self.account_id  = self.sts().current_account_id()
        self.region_name = self.sts().current_region_name()
        pass

    @cache
    def client(self):
        return Session().client('logs')

    @cache
    def sts(self):
        return STS()

    def destinations(self):
        return self.client().describe_destinations().get('destinations')

    def export_tasks(self):
        return self.client().describe_export_tasks().get('exportTasks')

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
        if self.log_group_not_exists(log_group_name=log_group_name):
            return status_error(f'log group does not exist: {log_group_name}')

        self.client().create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)
        return status_ok(message=f"log stream created ok: {log_stream_name}")

    def log_stream(self, log_group_name, log_stream_name):
        log_stream_arn = self.log_stream_arn(log_group_name=log_group_name, log_stream_name=log_stream_name)
        log_streams    = self.log_streams(log_group_name=log_group_name, log_stream_name_prefix=log_stream_name)
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

    def log_stream_not_exists(self, log_group_name, log_stream_name):
        return self.log_stream_exists(log_group_name=log_group_name, log_stream_name=log_stream_name) is False

    def log_streams(self, log_group_name, log_stream_name_prefix=None):
        if self.log_group_not_exists(log_group_name=log_group_name):
            #return status_error(f'log group does not exist: {log_group_name}')
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





