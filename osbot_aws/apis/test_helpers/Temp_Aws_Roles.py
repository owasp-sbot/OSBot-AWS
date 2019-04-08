from osbot_aws.helpers.IAM_Role import IAM_Role


class Temp_Aws_Roles:
    def __init__(self):
        self.temp_prefix                      = 'temp_role_'
        self.role_name__for_lambda_invocation = self.temp_prefix + 'for_lambda_invocation'
        pass

    def for_lambda_invocation(self):
        iam_role = IAM_Role(self.role_name__for_lambda_invocation)
        #iam_role.iam.role_delete()
        return iam_role.create_for__lambda().get('role_arn')