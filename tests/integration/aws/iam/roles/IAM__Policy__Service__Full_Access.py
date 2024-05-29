from unittest import TestCase

from osbot_aws.aws.iam.roles.IAM_Policy__Full_Access import IAM__Policy__Service__Full_Access
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Objects import obj_data


class test_IAM__Policy__Service__Full_Access(TestCase):

    def setUp(self):
        self.service_name           ='s3'
        self.expected_policy_name   = f"Policy__Full_Access__{self.service_name}"
        self.expected_statement     = { 'Version'  : '2012-10-17',
                                        'Statement': [{'Action'  : ['s3:*' ],
                                                       'Effect'  : 'Allow'  ,
                                                       'Resource': '*'}]    }
        self.iam_policy_full_access = IAM__Policy__Service__Full_Access(service_name=self.service_name)

    def test_create(self):
        with self.iam_policy_full_access as _:
            iam_policy    = _.iam_policy()
            iam_policy.create()
            assert iam_policy.exists() is True

    def test_iam_policy(self):
        with self.iam_policy_full_access as _:
            iam_policy  = _.iam_policy()
            account_id  = iam_policy.account_id

            assert iam_policy.statements == [self.expected_statement]

            assert obj_data(iam_policy) == { 'account_id'  : account_id                                                      ,
                                             'iam'         : str(iam_policy.iam)                                             ,
                                             'policy_arn'  : f'arn:aws:iam::{account_id}:policy/{self.expected_policy_name}' ,
                                             'policy_name' : self.expected_policy_name                                       ,
                                             'policy_path' : None                                                            ,
                                             'statements'  : str(iam_policy.statements)                                      ,
                                             'version'     : '2012-10-17'                                                    }

    def test_statement(self):
        with self.iam_policy_full_access as _:
            assert _.statement() == self.expected_statement
            assert _.policy_name == self.expected_policy_name
