from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.aws.iam.IAM_Role import IAM_Role


class Temp_Aws_Roles:
    def __init__(self):
        self.temp_prefix                      = 'temp_role_'
        self.role_name__for_lambda_invocation = self.temp_prefix + 'for_lambda_invocation' # todo: improve this logic
        pass

    def for_lambda_invocation__create(self, delete_existing=False):
        iam_role = IAM_Role(self.role_name__for_lambda_invocation)
        if delete_existing:
            iam_role.iam.role_delete()
        return iam_role.create_for__lambda().get('role_arn')

    def for_lambda_invocation__not_exists(self):
        return self.for_lambda_invocation_exists() is False

    def for_lambda_invocation_exists(self):
        iam_role = IAM_Role(self.role_name__for_lambda_invocation)
        return iam_role.iam.role_exists()

    def for_lambda_invocation__role_arn(self):
        account_id = AWS_Config().aws_session_account_id()
        role_name  = self.role_name__for_lambda_invocation
        return f"arn:aws:iam::{account_id}:role/{role_name}"
