from unittest import TestCase

from osbot_aws.apis.Cloud_Trail import Cloud_Trail
from osbot_aws.aws.boto3.View_Boto3_Rest_Calls import print_boto3_calls
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set, wait_for
from osbot_aws.aws.iam.IAM_Assume_Role import IAM_Assume_Role

TEMP_ROLE_NAME__ASSUME_ROLE = 'osbot_aws_temp_role__assume_role'
TEST_POLICY_DOCUMENT        = { "Version": "2012-10-17",
                                "Statement": [ { "Effect"  : "Allow"               ,
                                                 "Action"  : "s3:ListAllMyBuckets" ,
                                                 "Resource": "*"                  }]}
class test_IAM_Assume_Role(TestCase):

    def setUp(self):
        self.iam_assume_role = IAM_Assume_Role(role_name=TEMP_ROLE_NAME__ASSUME_ROLE)

    def test__init__(self):
        assert self.iam_assume_role.role_name        == TEMP_ROLE_NAME__ASSUME_ROLE

    def test_create_policy_document(self):
        expect_policy_document = { "Version": "2012-10-17",
                                   "Statement": [ { "Effect"  : "Allow"                   ,
                                                    "Action"  : "cloudtrail:LookupEvents" ,
                                                    "Resource": "*"                       }]}
        effect   = "Allow"
        service  = "cloudtrail"
        action   = "LookupEvents"
        resource = "*"
        kwargs = dict(effect=effect, service=service, action=action, resource=resource)
        assert self.iam_assume_role.create_policy_document(**kwargs) == expect_policy_document


    #@print_boto3_calls()
    def test_create_role(self):
        print()
        self.iam_assume_role.reset()                                        # reset cache (delete and create a new one)
        assert self.iam_assume_role.cached_role.cache_exists() is True      # check that cache doesn't exist

        self.iam_assume_role.delete_role()                                  # delete role
        assert self.iam_assume_role.role_exists()              is False     # check that cache doesn't exist

        self.iam_assume_role.create_role()                                  # create role

        assert self.iam_assume_role.cached_role.cache_exists() is True     # check that cache doesn't exist
        assert self.iam_assume_role.role_exists()              is True     # check that cache doesn't exist

        assert list_set(self.iam_assume_role.data()) == ['assume_policy','current_account_id','current_user_arn','current_user_id','policies', 'policies_to_add', 'result__credentials', 'result__role_create','role_arn','role_exists', 'role_name']
        assert self.iam_assume_role.role_exists() is True


    def test_credentials(self):
        credentials = self.iam_assume_role.credentials()
        assert list_set(credentials) == ['AccessKeyId', 'SecretAccessKey', 'SessionToken']

    def test_credentials_raw(self):
        credentials = self.iam_assume_role.credentials_raw()
        assert list_set(credentials) == ['AssumedRoleUser', 'Credentials']
        assert list_set(credentials['AssumedRoleUser']) == ['Arn', 'AssumedRoleId']
        assert list_set(credentials['Credentials'    ]) == ['AccessKeyId', 'Expiration', 'SecretAccessKey', 'SessionToken']

    def test_data(self):
        self.iam_assume_role.reset()
        assert self.iam_assume_role.data().get('role_name') == TEMP_ROLE_NAME__ASSUME_ROLE


    def test_default_assume_policy(self):
        assert self.iam_assume_role.default_assume_policy(                      ) == {'Version': '2012-10-17','Statement': []}
        assert self.iam_assume_role.default_assume_policy(user_arn='an_user_arn') == {'Version': '2012-10-17','Statement': [{'Action': 'sts:AssumeRole',
                                                                                                                             'Effect': 'Allow',
                                                                                                                             'Principal': {'AWS': 'an_user_arn'}}]}
        assert self.iam_assume_role.default_assume_policy(service_name='service') == {'Version': '2012-10-17','Statement': [{'Action': 'sts:AssumeRole',
                                                                                                                             'Effect': 'Allow',
                                                                                                                             'Principal': {'Service': 'service'}}]}
        assert self.iam_assume_role.default_assume_policy(federated='federated' ) == {'Version': '2012-10-17','Statement': [{'Action': 'sts:AssumeRole',
                                                                                                                             'Effect': 'Allow',
                                                                                                                             'Principal': {'Federated': 'federated'}}]}
        assert self.iam_assume_role.default_assume_policy(canonical_user='user' ) == {'Version': '2012-10-17','Statement': [{'Action': 'sts:AssumeRole',
                                                                                                                             'Effect': 'Allow',
                                                                                                                             'Principal': {'CanonicalUser': 'user'}}]}
        assert self.iam_assume_role.default_assume_policy(user_arn='an_user_arn',
                                                          service_name='service',
                                                          federated='federated',
                                                          canonical_user='user') == {'Version': '2012-10-17','Statement': [{'Action': 'sts:AssumeRole',
                                                                                                                            'Effect': 'Allow',
                                                                                                                            'Principal': {'AWS': 'an_user_arn'}},
                                                                                                                           {'Action': 'sts:AssumeRole',
                                                                                                                            'Effect': 'Allow',
                                                                                                                            'Principal': {'Service': 'service'}},
                                                                                                                           {'Action': 'sts:AssumeRole',
                                                                                                                            'Effect': 'Allow',
                                                                                                                            'Principal': {'Federated': 'federated'}},
                                                                                                                           {'Action': 'sts:AssumeRole',
                                                                                                                            'Effect': 'Allow',
                                                                                                                            'Principal': {'CanonicalUser': 'user'}}]}

    def test_policies(self):
        policies = self.iam_assume_role.policies()
        assert type(policies) == dict

    #@print_boto3_calls()
    def test_set_inline_policy(self):
        policy_name     = 'test_policy'
        policy_document = TEST_POLICY_DOCUMENT
        self.iam_assume_role.set_inline_policy(policy_name, policy_document)

        assert TEST_POLICY_DOCUMENT == {"Version": "2012-10-17",
                                        "Statement": [ { "Effect"   : "Allow"              ,
                                                         "Action"  : "s3:ListAllMyBuckets" ,
                                                         "Resource": "*"                   }]}

        policies = self.iam_assume_role.policies()
        assert policies[policy_name] == policy_document

        result = self.iam_assume_role.wait_for_valid_execution('s3', 'list_buckets')
        assert len(result.get('Buckets')) > 0



        s3_client             = self.iam_assume_role.boto3_client('s3')
        sts_client            = self.iam_assume_role.boto3_client('sts')
        user_identity         = sts_client.get_caller_identity()
        role_data             = self.iam_assume_role.data()
        current_account_id    = role_data.get('current_account_id')
        result__credentials   = role_data.get('result__credentials')
        assumed_role_user_arn = result__credentials.get('AssumedRoleUser').get('Arn')
        assumed_role_user_id  = result__credentials.get('AssumedRoleUser').get('AssumedRoleId')

        assert s3_client.meta.service_model.service_name  == 's3'
        assert sts_client.meta.service_model.service_name == 'sts'
        assert user_identity['Account']                   == current_account_id
        assert user_identity['Arn'    ]                   == assumed_role_user_arn
        assert user_identity['UserId' ]                   == assumed_role_user_id

        assert len(s3_client.list_buckets().get('Buckets')) > 0

    def test_role_arn(self):
        data     = self.iam_assume_role.data()
        role_arn = self.iam_assume_role.role_arn()
        assert role_arn == f"arn:aws:iam::{data.get('current_account_id')}:role/{self.iam_assume_role.role_name}"

    #@print_boto3_calls()
    def test_setup_data(self):
        self.iam_assume_role.reset()                                # deletes the cache
        setup_data = self.iam_assume_role.setup_data()
        assert list_set(setup_data) == [ 'assume_policy', 'current_account_id', 'current_user_arn','current_user_id','policies',
                                         'policies_to_add', 'result__credentials' , 'result__role_create',
                                         'role_arn','role_exists', 'role_name']
        assert self.iam_assume_role.cached_role.cache_exists() is True


class test_Cloud_Trail_Lookup(TestCase):

    #@print_boto3_calls(config__print_return_value=True)
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
        events = cloud_trail.events_in_last(50, page_size=1)
        assert list_set(next(events)) == ['AccessKeyId', 'CloudTrailEvent', 'EventId', 'EventName', 'EventSource', 'EventTime', 'ReadOnly', 'Resources', 'Username']


class test_DynamoDB__List_Tables(TestCase):

    def setUp(self):
        self.role_name = "temp_role__for_dynamo_db_access"

    #@print_boto3_calls(config__print_return_value=False)
    def test_1_get_dynamo_db_tables(self):

        policies_to_add = [dict(service="dynamodb", action="ListTables", resource="*")]
        iam_assume_role = IAM_Assume_Role(role_name=self.role_name, policies_to_add=policies_to_add)
        with iam_assume_role as _:
            _.create_role(recreate=True)
            client_dynamodb = _.boto3_client(service_name='dynamodb', region_name = 'eu-west-2')
            table_names     = client_dynamodb.list_tables().get('TableNames')
            assert len(table_names) > 1

    # #  todo: document better this bug: research more the interesting error that is happening when we quickly create and delete a role (the credentials work for a couple seconds and then stop working)
    # #  note: this test is commented out, but all passed ok when executed locally
    # #        the problem seems to happen when we do _.create_role(recreate=True) which creates and deletes a role very fast
    # def test_2_bug_race_condition_in_delete_and_create_role(self):
    #     iam_assume_role = IAM_Assume_Role(role_name=self.role_name)
    #     max_count = 10
    #     with pytest.raises(ClientError) as exc_info_1:
    #         with iam_assume_role as _:
    #             for i in range(max_count):
    #                 client_dynamodb = _.boto3_client(service_name='dynamodb', region_name='eu-west-2')
    #                 assert len(client_dynamodb.list_tables().get('TableNames')) > 0
    #                 wait_for(1)
    #                 print(f'ok after {i} seconds')
    #     print(f'failed after {i} seconds')
    #     assert ("An error occurred (AccessDeniedException)" in str(exc_info_1.value)) or ("UnrecognizedClientException"                            in str(exc_info_1.value))
    #     assert ("dynamodb:ListTables"                       in str(exc_info_1.value)) or ("The security token included in the request is invalid"  in str(exc_info_1.value))
    #     assert i != max_count
    #
    #     with pytest.raises(ClientError) as exc_info_2:
    #         with iam_assume_role as _:
    #             client_dynamodb_2 = _.boto3_client(service_name='dynamodb', region_name='eu-west-2')
    #             client_dynamodb_2.list_tables().get('TableNames')
    #     print(f'failed again on next request')
    #     assert ("An error occurred (AccessDeniedException)" in str(exc_info_2.value)) or ("UnrecognizedClientException"                            in str(exc_info_2.value))
    #     assert ("dynamodb:ListTables"                       in str(exc_info_2.value)) or ("The security token included in the request is invalid"  in str(exc_info_2.value))
    #
    #     # todo: find out for some reason this wasn't working, but the code is the same as test_3_bug_race_condition_in_delete_and_create_role
    #     #       maybe something to do with cached creds in current test?
    #     # wait_for(3)
    #     # iam_assume_role_2 = IAM_Assume_Role(role_name=self.role_name)
    #     # with iam_assume_role_2 as _:
    #     #     _.credentials_reset()
    #     #     client_dynamodb_3 = _.boto3_client(service_name='dynamodb', region_name='eu-west-2')
    #     #     client_dynamodb_3.list_tables().get('TableNames')
    #     # print('ok after reseting credentials')
    #
    # def test_3_bug_race_condition_in_delete_and_create_role(self):
    #     iam_assume_role = IAM_Assume_Role(role_name=self.role_name)
    #     with iam_assume_role as _:
    #         _.credentials_reset()
    #         client_dynamodb_3 = _.boto3_client(service_name='dynamodb', region_name='eu-west-2')
    #         client_dynamodb_3.list_tables().get('TableNames')
    #     print('ok after reseting credentials')