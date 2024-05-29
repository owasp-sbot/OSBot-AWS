from osbot_aws.aws.iam.IAM_Policy                            import IAM_Policy
from osbot_aws.aws.iam.roles.IAM__Statement__Resource__Allow import IAM__Statement__Resource__Allow

class IAM__Policy__Service__Full_Access(IAM__Statement__Resource__Allow):
    policy_name : str

    def __init__(self, service_name):
        actions  = [f'{service_name}:*']
        resource = '*'
        self.policy_name = f"Policy__Full_Access__{service_name}"
        super().__init__(actions=actions, resource=resource)

    def arn(self):
        return self.iam_policy().policy_arn

    def iam_policy(self):
        return IAM_Policy(policy_name=self.policy_name, statements=[self.statement()])

    def create(self):
        return self.iam_policy().create()