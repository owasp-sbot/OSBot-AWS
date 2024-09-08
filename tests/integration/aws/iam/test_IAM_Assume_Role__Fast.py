from unittest import TestCase

from osbot_aws.aws.iam.IAM_Assume_Role              import IAM_Assume_Role
from osbot_utils.utils.Misc                         import list_set
from tests.integration.aws.iam.test_IAM_Assume_Role import TEMP_ROLE_NAME__ASSUME_ROLE


# todo: fix the fact that the role TEMP_ROLE_NAME__ASSUME_ROLE (i.e. osbot_aws_temp_role__assume_role) needs this Trust Relationship added manually
# {
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Effect": "Allow",
#             "Principal": {
#                 "AWS": [
#                     "arn:aws:iam::470426667096:user/OSBot-AWS-Dev__Only-IAM",
#                     "arn:aws:iam::470426667096:user/dinis.cruz+aws@owasp.org"
#                 ]
#             },
#             "Action": "sts:AssumeRole"
#         }
#     ]
# }

class test_IAM_Assume_Role__Fast(TestCase):
    iam_assume_role : IAM_Assume_Role

    @classmethod
    def setUpClass(cls):
        cls.iam_assume_role = IAM_Assume_Role(role_name=TEMP_ROLE_NAME__ASSUME_ROLE)
        cls.iam_assume_role.create_role()

    def test__init__(self):
        assert self.iam_assume_role.role_name        == TEMP_ROLE_NAME__ASSUME_ROLE

    def test___setup_data(self):                                     # this needs to be the first one to execute
        #self.iam_assume_role.reset()                                # deletes the cache
        setup_data = self.iam_assume_role.setup_data()
        assert list_set(setup_data) == [ 'assume_policy', 'current_account_id', 'current_user_arn','current_user_id','policies',
                                         'policies_to_add', 'result__credentials' , 'result__role_create',
                                         'role_arn','role_exists', 'role_name']
        assert self.iam_assume_role.cached_role.cache_exists() is True


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

    def test_credentials_raw(self):
        credentials = self.iam_assume_role.credentials_raw()
        assert list_set(credentials) == ['AssumedRoleUser', 'Credentials']
        assert list_set(credentials['AssumedRoleUser']) == ['Arn', 'AssumedRoleId']
        assert list_set(credentials['Credentials'    ]) == ['AccessKeyId', 'Expiration', 'SecretAccessKey', 'SessionToken']

    def test_data(self):
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




    def test_role_arn(self):
        data     = self.iam_assume_role.data()
        role_arn = self.iam_assume_role.role_arn()
        assert role_arn == f"arn:aws:iam::{data.get('current_account_id')}:role/{self.iam_assume_role.role_name}"

