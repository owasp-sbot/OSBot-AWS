from osbot_aws.apis.IAM         import IAM
from osbot_aws.helpers.IAM_Role import IAM_Role

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
        iam_role = IAM_Role(self.role_name__for_lambda_invocation)
        return iam_role.iam.role_not_exists()

    def for_lambda_invocation__role_arn(self):
        return 'arn:aws:iam::{0}:role/{1}'.format(IAM().account_id(),self.role_name__for_lambda_invocation)
