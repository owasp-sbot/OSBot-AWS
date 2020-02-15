import datetime
from osbot_aws.apis.Boto_Helpers import Boto_Helpers
from osbot_aws.apis.S3 import S3
from osbot_aws.apis.Session import Session


class Cloud_Trail(Boto_Helpers):

    def __init__(self):
        self.cloudtrail = Session().client('cloudtrail')
        self.s3         = S3()

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

    def trail(self, trail_name):
        trail        = self.cloudtrail.get_trail(Name=trail_name).get('Trail')
        trail_status = self.cloudtrail.get_trail_status(Name=trail_name)        # also get the trail status
        trail.update(trail_status)                                              # add its values to the trail object
        del trail['ResponseMetadata']                                           # remove the ResponseMetadata since we don't need this value
        return trail

    def trail_create(self, trail_name, account_id, region, s3_bucket, s3_key_prefix):
        self.trail_s3_bucket_configure(trail_name, s3_bucket, account_id, region)       # create and configure bucket
        self.trail_create_raw(trail_name, s3_bucket, s3_key_prefix)                                 # create trail
        self.trail_start(trail_name)                                                                # enable it
        return self.trail(trail_name)                                                               # return trail details

    def trail_create_raw(self, trail_name, s3_bucket, s3_key_prefix, sns_topic_name=None, global_service_events=True, multi_region_trail=True, log_file_verification=True):
        params = {  'Name'                      : trail_name,
                    'S3BucketName'              : s3_bucket,
                    'S3KeyPrefix'               : s3_key_prefix,
                    'IncludeGlobalServiceEvents': global_service_events,
                    'IsMultiRegionTrail'        : multi_region_trail,
                    'EnableLogFileValidation'   : log_file_verification
        }
        if sns_topic_name:
            params['SnsTopicName'] = sns_topic_name
        try:
            return self.cloudtrail.create_trail(**params)
        except Exception as error:
            return { 'error': f'{error}'}

    def trail_delete(self, trail_name):
        self.cloudtrail.delete_trail(Name=trail_name)
        return self

    def trail_status(self,trail_name):
        return self.cloudtrail.get_trail_status(Name=trail_name)

    def trail_s3_bucket_configure(self, trail_name, s3_bucket, account_id, region):
        resource_arn = self.s3.policy_statements__resource_arn(s3_bucket, trail_name, account_id)
        statements   = self.s3.policy_statements__without(s3_bucket, 'Resource', resource_arn) # making sure we are not adding the same resource_arn twice
        statement    = self.s3.policy_statements__new('s3:PutObject', 'Allow', 'cloudtrail.amazonaws.com', resource_arn)
        statements.append(statement)

        self.s3.bucket_create(s3_bucket, region)                # make sure bucket exists
        self.s3.policy_create(s3_bucket,statements)             # add cloud trail policy
        return self

    def trail_start(self, trail_name):
        self.cloudtrail.start_logging(Name=trail_name)
        return self

    def trail_stop(self, trail_name):
        return self.cloudtrail.stop_logging(Name=trail_name)

    def trails(self):
        return self.cloudtrail.list_trails().get('Trails')
