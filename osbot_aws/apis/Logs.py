import boto3

from osbot_aws.apis.Boto_Helpers import Boto_Helpers


class Logs(Boto_Helpers):
    def __init__(self,log_group_name, stream_name):
        self.log_group_name = log_group_name
        self.stream_name    = stream_name
        self._logs          = None

    def logs(self):
        if self._logs is None:
            self._logs = boto3.client('logs')
        return self._logs

    def group_create(self):
        if self.group_exists(): return True
        self.logs().create_log_group(logGroupName=self.log_group_name)
        return self.group_exists()

    def group_delete(self):
        if self.group_exists() is False: return False
        self.logs().delete_log_group(logGroupName=self.log_group_name)
        return self.group_exists() is False

    def group_exists(self):
        return self.group_info() is not None

    def group_info(self):
        for log_group in self.logs().describe_log_groups(logGroupNamePrefix= self.log_group_name).get('logGroups'):
            if log_group.get('logGroupName') == self.log_group_name:
                return log_group
        return None

    def groups(self):
        groups = {}
        for group in  self.invoke_using_paginator(self.logs(), 'describe_log_groups', 'logGroups'):
            groups[group.get('logGroupName')] = group
        return groups

    def stream_create(self):
        if self.stream_exists() is True: return False
        self.logs().create_log_stream(logGroupName=self.log_group_name, logStreamName= self.stream_name)
        return self.stream_exists()

    def stream_delete(self):
        if self.stream_exists() is False: return False
        self.logs().delete_log_stream(logGroupName=self.log_group_name, logStreamName= self.stream_name)
        return self.stream_exists() is False

    def stream_exists(self):
        return len(self.streams()) > 0

    def streams(self):
        return self.logs().describe_log_streams(logGroupName=self.log_group_name, logStreamNamePrefix=self.stream_name).get('logStreams')

    def get_messages(self,group_name, stream_name):
        messages = []
        for event in self.logs().get_log_events(logGroupName=group_name, logStreamName=stream_name).get('events'):
            messages.append(event.get('message'))
        return messages