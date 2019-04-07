from unittest import TestCase

from pbx_gs_python_utils.utils.Dev import Dev

from osbot_aws.apis.IAM import IAM
from osbot_aws.apis.test_helpers.Temp_Aws_Roles import Temp_Aws_Roles


class test_Temp_Aws_Roles(TestCase):
    def setUp(self):
        self.iam            = IAM()
        self.temp_aws_roles = Temp_Aws_Roles()
        self.account_id     = '244560807427'

    def test_for_lambda_invocation(self):
        role_name = self.temp_aws_roles.role_name__for_lambda_invocation
        role_arn  = 'arn:aws:iam::{0}:role/{1}'.format(self.account_id, role_name)
        assert role_arn == self.temp_aws_roles.for_lambda_invocation()