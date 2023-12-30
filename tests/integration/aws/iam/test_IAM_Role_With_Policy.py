import pytest
from pprint                                 import pprint
from unittest                               import TestCase
from osbot_utils.utils.Misc                 import random_string
from osbot_aws.AWS_Config                   import AWS_Config
from osbot_aws.aws.iam.IAM_Role_With_Policy import IAM_Role_With_Policy


@pytest.mark.skip('Wire up tests')
class test_IAM_Role_With_Policy(TestCase):
    def setUp(self):
        self.temp_role_name       = f"osbot_temp_role_{random_string()}"
        self.iam_role_with_policy = IAM_Role_With_Policy(self.temp_role_name)
        with AWS_Config() as aws_config:
            self.account_id  = aws_config.aws_session_account_id()
            self.region      = aws_config.aws_session_region_name()

    def tearDown(self) -> None:
        self.iam_role_with_policy.delete()
        assert self.iam_role_with_policy.not_exists()

    def test__init__(self):
        assert self.iam_role_with_policy.role_name == self.temp_role_name

    def test_create_api_gateway__cloudwatch_allow_all(self):
        policy_name = "Cloud_Watch"
        project_name = self.temp_role_name
        result = self.iam_role_with_policy.create_api_gateway__cloudwatch_allow_all(project_name)
        assert result == {'policies_arns': [f'arn:aws:iam::{self.account_id}:policy/{policy_name}_{project_name}'],
                          'role_arn': f'arn:aws:iam::{self.account_id}:role/{project_name}'}
        pprint(result)