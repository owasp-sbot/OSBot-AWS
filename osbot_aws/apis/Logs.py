import calendar
import datetime
import time

from osbot_aws.apis.Boto_Helpers import Boto_Helpers
from osbot_aws.apis.Session import Session
from osbot_utils.decorators.lists.index_by import index_by
from osbot_utils.utils.Misc import list_set, timestamp_utc_now, wait


class Logs(Boto_Helpers):

    def __init__(self, group_name=None, stream_name=None):  # refactor class to new pattern where these values are not provided here in the ctor
        self.log_group_name = group_name
        self.stream_name    = stream_name
        self._logs          = None

    # helper methods
    def client(self):
        if self._logs is None:
            self._logs = Session().client('logs')
        return self._logs

    # main methods

    def create(self):
        self.group_create()
        self.stream_create()
        return self

    def event_add(self, message, timestamp=None, sequence_token=None):
        if timestamp is None: timestamp = timestamp_utc_now()
        return self.events_add([{'message': message, 'timestamp':timestamp}], sequence_token)

    def events_add(self, events, sequence_token=None):
        try:
            if sequence_token:
                result  = self.client().put_log_events(logGroupName=self.log_group_name,logStreamName=self.stream_name,logEvents=events, sequenceToken=sequence_token)
            else:
                result  = self.client().put_log_events(logGroupName=self.log_group_name,logStreamName=self.stream_name,logEvents=events)
            next_sequence_token = result.get('nextSequenceToken')
            if result.get('rejectedLogEventsInfo') is not None:
                return {'status': 'error', 'nextSequenceToken' : next_sequence_token, 'data': result.get('rejectedLogEventsInfo')}
            return {'status': 'ok', 'nextSequenceToken' : next_sequence_token}
        except Exception as error:
            return {'status': 'error', 'data': '{0}'.format(error)}


    def events(self):
        return self.client().get_log_events(logGroupName=self.log_group_name, logStreamName=self.stream_name)

    def group_create(self):
        if self.group_exists(): return False
        self.client().create_log_group(logGroupName=self.log_group_name)
        return self.group_exists()

    def group_delete(self):
        if self.group_exists() is False: return False
        self.client().delete_log_group(logGroupName=self.log_group_name)
        return self.group_exists() is False

    def group_exists(self):
        return self.group_info() is not None

    def group_events(self, log_stream_prefix=None, start_time=None, end_time=None, filter_pattern=None, limit=None):
        kwargs = {"logGroupName": self.log_group_name}
        if log_stream_prefix:
            kwargs['logStreamNamePrefix'] = log_stream_prefix
        if start_time:
            kwargs['startTime'] = start_time
        if end_time:
            kwargs['endTime'] = end_time
        if filter_pattern:
            kwargs['filterPattern'] = filter_pattern
        if limit:
            kwargs['limit'] = limit

        return self.client().filter_log_events(**kwargs).get('events')

    def group_events_wait_for_pattern(self,log_stream_prefix=None, filter_pattern=None, sleep_for=0.5, max_attempts=20):
        if self.group_wait_until_exists():
            for i in range(0,max_attempts):
                events = self.group_events(log_stream_prefix=log_stream_prefix, filter_pattern=filter_pattern)
                if len(events) > 0:
                    return events
                #print('group_events_wait_for_pattern', i,sleep_for)
                wait(sleep_for)
        return []

    def group_info(self):
        for log_group in self.client().describe_log_groups(logGroupNamePrefix= self.log_group_name).get('logGroups'):
            if log_group.get('logGroupName') == self.log_group_name:
                return log_group
        return None

    def group_messages(self, log_stream_prefix=None, start_time=None, end_time=None, filter_pattern=None, limit=None):
        messages = []
        if self.group_wait_until_exists():
            events = self.group_events(log_stream_prefix=log_stream_prefix,start_time=start_time,end_time=end_time,filter_pattern=filter_pattern, limit=limit)
            for event in events:
                messages.append(event.get('message'))
        return messages

    def group_messages_wait_for_pattern(self, log_stream_prefix=None, filter_pattern=None):
        messages = []
        events = self.group_events_wait_for_pattern(log_stream_prefix=log_stream_prefix,filter_pattern=filter_pattern)
        for event in events:
            messages.append(event.get('message'))
        return messages

    def group_wait_until_exists(self, sleep_for = 0.5, max_attempts = 60):
        for i in range(0,max_attempts):
            if self.group_exists():
                return True
            #print('group_wait_until_exists', i,sleep_for)
            wait(sleep_for)
        return False

    @index_by
    def groups(self):
        return list(self.invoke_using_paginator(self.client(), 'describe_log_groups', 'logGroups'))
        #groups = {}
        #for group in
        #    groups[group.get('logGroupName')] = group
        #return groups

    def groups_names(self):
        return list_set(self.groups(index_by='logGroupName'))

    def name(self):
        return self.log_group_name

    def stream_create(self):
        if self.stream_exists() is True: return False
        self.client().create_log_stream(logGroupName=self.log_group_name, logStreamName= self.stream_name)
        return self.stream_exists()

    def stream_delete(self):
        if self.stream_exists() is False: return False
        self.client().delete_log_stream(logGroupName=self.log_group_name, logStreamName= self.stream_name)
        return self.stream_exists() is False

    def stream_exists(self):
        return len(self.streams()) > 0

    def streams(self):
        if self.stream_name is None:
            return self.client().describe_log_streams(logGroupName=self.log_group_name).get('logStreams')
        return self.client().describe_log_streams(logGroupName=self.log_group_name, logStreamNamePrefix=self.stream_name).get('logStreams')

    def messages(self,limit=10000, hours=24, start_time=None, end_time=None, max_loop=25):

        if start_time is None:
            start_time = int((datetime.datetime.now() - datetime.timedelta(hours=hours)).timestamp() * 1000)

        if end_time is None:
            end_time = int(time.time() * 1000)

        # kwargs = dict(  logGroupName  = self.log_group_name ,
        #                 logStreamName = self.stream_name    ,
        #                 limit         = limit               ,
        #                 startTime     = start_time          ,
        #                 endTime       = end_time            )
        # response  = self.client().get_log_events(**kwargs)
        # #events = self.invoke_using_paginator(self.client(), 'get_log_events', 'events', **kwargs)


        params = {
            "logGroupName": self.log_group_name ,
            "logStreamName": self.stream_name   ,
            "startFromHead": True               ,
            "startTime"    : start_time         ,
            "endTime"      : end_time           ,
            "limit"        : limit              }

        log_events = []
        import logging
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        while max_loop > 0:
            logger.info(f"Fetching log events with params: {params}")
            response = self.client().get_log_events(**params)
            events   = response["events"]
            log_events.extend(events)
            next_token = response.get("nextForwardToken")
            logger.info(f"Got {len(events)} events with next_token: {next_token}")
            #print(f'limit:{limit} len(log_events):{len(log_events)}')
            if len(events) == 0:
                break
            if next_token == params.get("nextToken"):
                break
            if len (log_events) >= limit:
                break
            params['nextToken'] = next_token
            max_loop -=1

        messages = []
        for event in log_events:
            messages.append(event.get('message'))
        return messages

    def __repr__(self):
        return f"Logs: {self.log_group_name or ''} {self.stream_name or ''}"