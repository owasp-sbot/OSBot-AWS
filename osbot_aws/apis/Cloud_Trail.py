import datetime
from osbot_aws.apis.Boto_Helpers import Boto_Helpers
from osbot_aws.apis.Session import Session


class Cloud_Trail(Boto_Helpers):

    def __init__(self):
        self.cloudtrail = Session().client('cloudtrail')

    # helpers
    def date_now(self):
        return datetime.datetime.utcnow()

    def date_minutes_ago(self, minutes):
        return datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes)


    def events(self,start_time, end_time, max_results=50):
        return self.cloudtrail.lookup_events(LookupAttributes=[], StartTime=start_time,EndTime=end_time,MaxResults=max_results).get('Events')

    def events_all(self, start_time, end_time):
        return Boto_Helpers.invoke_using_paginator(self.cloudtrail,'lookup_events','Events', LookupAttributes=[], StartTime=start_time,EndTime=end_time)

    def events_in_last(self,minutes):
        end_time   = self.date_now()
        start_time = self.date_minutes_ago(minutes)
        return self.events_all(start_time, end_time)

    def tags(self, resource_ids=[]):
        return self.cloudtrail.list_tags(ResourceIdList=resource_ids)

    def trail_create(self, name, s3_bucket, s3_key_prefix, sns_topic_name=None, global_service_events=True, multi_region_trail=True, log_file_verification=False):
        params = {  'Name':name,
                    'S3BucketName':s3_bucket,
                    'S3KeyPrefix':s3_key_prefix,
                    'IncludeGlobalServiceEvents':global_service_events,
                    'IsMultiRegionTrail':multi_region_trail,
                    'EnableLogFileValidation':log_file_verification
        }
        if sns_topic_name:
            params['SnsTopicName'] = sns_topic_name
        try:
            return self.cloudtrail.create_trail(**params)
        except Exception as error:
            return { 'error': f'{error}'}

    def trails(self):
        return self.cloudtrail.list_trails().get('Trails')
