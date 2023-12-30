from osbot_utils.utils.Dev import pformat

from osbot_aws.aws.iam.IAM import IAM


class IAM_Policy:
    def __init__(self, policy_name=None, statements=None, policy_path=None, policy_arn=None):
        self.iam         = IAM()
        self.policy_name = policy_name
        self.version     = "2012-10-17"
        self.statements  = statements or []
        self.policy_path = policy_path
        self.account_id  = self.iam.account_id()
        self.policy_arn  = policy_arn or self.iam.policy_arn(self.policy_name, self.policy_path, self.account_id)

    def add_cloud_watch(self, resource_arn):
        return self.add_statement_allow(["logs:CreateLogGroup","logs:CreateLogStream","logs:PutLogEvents"], [resource_arn])

    def add_statement(self, effect, actions, resources):
        self.statements.append({"Effect"   : effect    ,
                                "Action"   : actions   ,
                                "Resource" : resources})
        return self

    def add_statement_allow(self, actions, resources):
        return self.add_statement('Allow', actions,resources)

    def create(self,delete_before_create=False):
        if self.policy_name is None:
            return {'status':'error', 'data':'policy name is None'}
        return self.iam.policy_create(self.policy_name, self.statement(), delete_before_create=delete_before_create)

    def delete(self):
        return self.iam.policy_delete(self.policy_arn)

    def exists(self):
        return self.iam.policy_exists(self.policy_arn)

    def statement(self):
        return { 'Version' : self.version , 'Statement': self.statements}

    def statement_from_aws(self):
        return self.iam.policy_statement(self.policy_arn)

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.policy_name} \n { pformat(self.statements)}"
