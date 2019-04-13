import calendar
import datetime
import time

import boto3
import botocore
from pbx_gs_python_utils.utils.Dev import Dev

from osbot_aws.apis.Boto_Helpers import Boto_Helpers
from osbot_aws.apis.Session import Session


class Logs(Boto_Helpers):
    def __init__(self, group_name, stream_name=None):
        self.log_group_name = group_name
        self.stream_name    = stream_name
        self._logs          = None

    # helper methods
    def logs(self):
        if self._logs is None:
            self._logs = Session().client('logs')
        return self._logs

    def timestamp_utc_now(self):        # bug: this is not working 100% (I'm getting 1h early)
        #calendar.timegm(time.gmtime())
        return int(datetime.datetime.utcnow().strftime('%s')) * 1000

    # main methods

    def create(self):
        self.group_create()
        self.stream_create()
        return self

    def event_add(self, message, timestamp=None, sequence_token=None):
        if timestamp is None: timestamp = self.timestamp_utc_now()
        return self.events_add([{'message': message, 'timestamp':timestamp}], sequence_token)

    def events_add(self, events, sequence_token=None):
        try:
            if sequence_token:
                result  = self.logs().put_log_events(logGroupName=self.log_group_name,logStreamName=self.stream_name,logEvents=events, sequenceToken=sequence_token)
            else:
                result  = self.logs().put_log_events(logGroupName=self.log_group_name,logStreamName=self.stream_name,logEvents=events)
            nextSequenceToken = result.get('nextSequenceToken')
            if result.get('rejectedLogEventsInfo') is not None:
                return {'status': 'error', 'nextSequenceToken' : nextSequenceToken, 'data': result.get('rejectedLogEventsInfo')}
            return {'status': 'ok', 'nextSequenceToken' : nextSequenceToken}
        except Exception as error:
            return {'status': 'error', 'data': '{0}'.format(error)}


    def events(self):
        return self.logs().get_log_events(logGroupName=self.log_group_name, logStreamName=self.stream_name)

    def group_create(self):
        if self.group_exists(): return False
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
        if self.stream_name is None:
            return self.logs().describe_log_streams(logGroupName=self.log_group_name).get('logStreams')
        return self.logs().describe_log_streams(logGroupName=self.log_group_name, logStreamNamePrefix=self.stream_name).get('logStreams')

    def messages(self):
        messages = []
        for event in self.logs().get_log_events(logGroupName=self.log_group_name, logStreamName=self.stream_name).get('events'):
            messages.append(event.get('message'))
        return messages