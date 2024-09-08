import datetime
import json

from osbot_utils.decorators.lists.group_by  import group_by
from osbot_utils.decorators.lists.index_by  import index_by
from osbot_utils.utils.Json                 import json_parse
from osbot_aws.apis.Boto_Helpers            import Boto_Helpers
from osbot_aws.aws.s3.S3                    import S3
from osbot_aws.apis.Session                 import Session


class Cloud_Trail(Boto_Helpers):                # todo write tests for this class (which was lost in a past refactor)

    def __init__(self):
        self.cloudtrail = Session().client('cloudtrail')
        self.s3         = S3()

    # helpers
    def date_now(self):
        return datetime.datetime.utcnow()

    def date_minutes_ago(self, minutes):
        return datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes)

    def event_selectors(self, trail_name):
        return  self.cloudtrail.get_event_selectors(TrailName=trail_name).get('EventSelectors')

    def events(self, start_time, end_time, max_results=50, lookup_attributes=None):
        kwargs = {
            'LookupAttributes': lookup_attributes or [],
            'StartTime'       : start_time              ,
            'EndTime'         : end_time                ,
            'MaxResults'      : max_results
        }
        return self.cloudtrail.lookup_events(**kwargs).get('Events')

    def events_all(self, start_time, end_time, lookup_attributes=None, page_size=None):
        kwargs = {  'api'             : self.cloudtrail         ,
                    'method'          : 'lookup_events'         ,
                    'field_id'        : 'Events'                ,
                    'LookupAttributes': lookup_attributes or [] ,
                    'StartTime'       : start_time              ,
                    'EndTime'         : end_time                }
        if page_size:
            kwargs['MaxResults'] = page_size
        return Boto_Helpers.invoke_using_paginator(**kwargs)

    def events_in_last(self,minutes, lookup_attributes=None, page_size=None):
        end_time   = self.date_now()
        start_time = self.date_minutes_ago(minutes)
        return self.events_all(start_time, end_time, lookup_attributes=lookup_attributes, page_size=page_size)

    @index_by
    @group_by
    def convert_to_cloud_trail_events(self, events):
        for event in events:
            cloud_trail_event = json_parse(event.get('CloudTrailEvent', {}))
            yield cloud_trail_event
    def tags(self, resource_ids=[]):
        return self.cloudtrail.list_tags(ResourceIdList=resource_ids)

    def log_files(self, trail_name, account_id, region, year, month, day):
        trail         = self.trail(trail_name)
        log_type      = 'CloudTrail'
        s3_bucket     = trail.get('S3BucketName')
        s3_key_prefix = trail.get('S3KeyPrefix')
        s3_prefix     = f'{s3_key_prefix}/AWSLogs/{account_id}/'                           \
                        f'{log_type}/{region}/{year}/{month}/{day}/'
        s3_files      = self.s3.find_files(s3_bucket, prefix=s3_prefix)
        return s3_files

    def log_files_records(self, trail_name, log_files):
        trail     = self.trail(trail_name)
        s3_bucket = trail.get('S3BucketName')
        records   = []
        for log_file in log_files:
            contents = self.s3.file_contents_from_gzip(s3_bucket, log_file)
            records.extend(json.loads(contents).get('Records'))
        return records

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

        self.s3.bucket_create(s3_bucket, region)                # make sure bucket exists
                                                                # see https://docs.aws.amazon.com/awscloudtrail/latest/userguide/create-s3-bucket-policy-for-cloudtrail.html
        resource_arn = self.s3.policy_statements__resource_arn(s3_bucket, trail_name, account_id)
        statements   = self.s3.policy_statements__without(s3_bucket, 'Resource', resource_arn) # making sure we are not adding the same resource_arn twice
        statement    = self.s3.policy_statements__new('s3:PutObject', 'Allow', 'cloudtrail.amazonaws.com', resource_arn)
        statements.append(statement)
        if 's3:GetBucketAcl' not in self.s3.policy_statements(s3_bucket, index_by='Action'):
            statements.append(self.s3.policy_statements__new('s3:GetBucketAcl', 'Allow', 'cloudtrail.amazonaws.com', f"arn:aws:s3:::{s3_bucket}"))

        self.s3.policy_create(s3_bucket,statements)             # add cloud trail policy
        return self

    def trail_start(self, trail_name):
        self.cloudtrail.start_logging(Name=trail_name)
        return self

    def trail_stop(self, trail_name):
        return self.cloudtrail.stop_logging(Name=trail_name)

    def trails(self):
        return self.cloudtrail.list_trails().get('Trails')
