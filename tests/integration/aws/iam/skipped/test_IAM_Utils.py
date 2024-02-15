import pytest
from unittest                                   import TestCase
from osbot_aws.apis.test_helpers.Temp_Lambda    import Temp_Lambda
from osbot_utils.utils.Dev                      import pprint
from osbot_aws.aws.iam.IAM_Policy               import IAM_Policy
from osbot_aws.aws.iam.IAM_Role                 import IAM_Role
from osbot_aws.aws.iam.IAM_Utils                import IAM_Utils


@pytest.mark.skip('Wire up tests')
class test_IAM_Utils(TestCase):

    def setUp(self) -> None:
        self.iam_utils = IAM_Utils()

    def test_lambda_policy_service_sqs(self):
        iam_policy = IAM_Policy(policy_arn=self.iam_utils.arn_aws_policy_service_sqs_lambda)
        pprint(iam_policy.exists())

    def test_policy_add_sqs_permissions_to_lambda_role(self):
        policy_name = self.iam_utils.arn_aws_policy_service_sqs_lambda.split('/').pop(-1)
        with Temp_Lambda() as temp_lambda:
            lambda_name = temp_lambda.lambda_name
            iam_role_name = self.iam_utils.policy_add_sqs_permissions_to_lambda_role(lambda_name)
            iam_role = IAM_Role(role_name=iam_role_name)
            pprint(iam_role.info())
            assert policy_name       in iam_role.policies_statements()
            assert iam_role.exists() is True

            self.iam_utils.policy_remove_sqs_permissions_to_lambda_role(lambda_name)

            assert policy_name       not in iam_role.policies_statements()