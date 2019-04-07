import boto3

from pbx_gs_python_utils.utils.Dev import Dev
from pbx_gs_python_utils.utils.aws.Boto_Helpers import Boto_Helpers


class Logs(Boto_Helpers):
    def __init__(self):
        self.logs       = boto3.client('logs')

    def group_create(self, name):
        self.logs.create_log_group(logGroupName=name)
        return self

    def group_delete(self, name):
        self.logs.delete_log_group(logGroupName=name)
        return self

    def group_exists(self, name):
        return self.group_details(name) is not None

    def group_details(self, name):
        for log_group in self.logs.describe_log_groups(logGroupNamePrefix= name).get('logGroups'):
            if log_group.get('logGroupName') == name:
                return log_group
        return None

    def groups(self):
        groups = {}
        for group in  self.invoke_using_paginator(self.logs, 'describe_log_groups', 'logGroups'):
            groups[group.get('logGroupName')] = group
        return groups

    def get_messages(self,group_name, stream_name):
        messages = []
        for event in self.logs.get_log_events(logGroupName=group_name, logStreamName=stream_name).get('events'):
            messages.append(event.get('message'))
        return messages