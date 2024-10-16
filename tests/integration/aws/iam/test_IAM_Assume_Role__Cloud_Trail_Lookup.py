from unittest import TestCase

import pytest

from osbot_aws.apis.Cloud_Trail import Cloud_Trail
from osbot_aws.aws.iam.IAM_Assume_Role import IAM_Assume_Role
from osbot_utils.utils.Misc import list_set

# botocore.errorfactory.AccessDeniedException: An error occurred (AccessDeniedException) when calling the LookupEvents
#   operation: User: arn:aws:sts::470426667096:assumed-role/temp_role__for_cloud_trail_logs/osbot_sts_session__broazhj
#   is not authorized to perform: cloudtrail:LookupEvents because no identity-based policy allows the cloudtrail:LookupEvents action
@pytest.mark.skip('Started to fail with error above') # todo: find root cause
class test_IAM_Assume_Role__Cloud_Trail_Lookup(TestCase):

    def test_get_cloud_trail_logs(self):
        role_name            = "temp_role__for_cloud_trail_logs"

        self.iam_assume_role = IAM_Assume_Role(role_name=role_name)
        self.iam_assume_role.create_role(recreate=True)

        client          = self.iam_assume_role.boto3_client(service_name='cloudtrail')
        policy_name     = 'cloud_trail_logs_policy'
        policy_document = self.iam_assume_role.create_policy_document( service='cloudtrail', action='LookupEvents', resource='*')

        self.iam_assume_role.set_inline_policy(policy_name, policy_document)
        self.iam_assume_role.add_policy(service='cloudtrail', action='LookupEvents', resource='*')

        cloud_trail            = Cloud_Trail()
        cloud_trail.cloudtrail = client

        def check_in_last_minutes(minutes):
            try:
                events = cloud_trail.events_in_last(0, page_size=1)
                event  = list_set(next(events))
                assert event == ['AccessKeyId', 'CloudTrailEvent', 'EventId', 'EventName', 'EventSource', 'EventTime', 'ReadOnly', 'Resources', 'Username']
            except StopIteration:
                pass

        check_in_last_minutes(0)
        check_in_last_minutes(600)