import unittest
from unittest import TestCase

from osbot_utils.utils.Dev import Dev

from osbot_aws.AWS_Config import AWS_Config

from osbot_aws.apis.IAM import IAM
from osbot_aws.apis.test_helpers.Temp_Aws_Roles import Temp_Aws_Roles


class test_Temp_Aws_Roles(TestCase):
    def setUp(self):
        self.temp_aws_roles = Temp_Aws_Roles()
        self.account_id     = '244560807427'

    def test_for_lambda_invocation__role_arn(self):
        account_id = AWS_Config().aws_session_account_id()
        role_arn   = self.temp_aws_roles.for_lambda_invocation__role_arn()
        assert role_arn == f"arn:aws:iam::{account_id}:role/temp_role_for_lambda_invocation"

    @unittest.skip('causes side effect with other tests, due to the fact that AWS takes a while to sync the privileges internally')
    def create_test_for_lambda_invocation(self):
        role_name = self.temp_aws_roles.role_name__for_lambda_invocation
        role_arn  = 'arn:aws:iam::{0}:role/{1}'.format(self.account_id, role_name)
        assert role_arn == self.temp_aws_roles.for_lambda_invocation__role_arn(delete_existing=True)
        self.iam = IAM().set_role_name(role_name)
        policies_statements = self.iam.role_policies_statements(just_statements=True)
        resource = policies_statements[0].get('Resource')[0]
        assert self.account_id in resource                          # confirm account_id value is in there (regression test for bug)

