from pbx_gs_python_utils.utils.Dev import Dev

from osbot_aws.apis.IAM import IAM


class IAM_Policy:
    def __init__(self, policy_name=None):
        self.iam         = IAM()
        self.policy_name = policy_name
        self.version     = "2012-10-17"
        self.statements  = []

    def add_cloud_watch(self, resource_arn):
        return self.add_statement_allow(["logs:CreateLogStream","logs:PutLogEvents"], [resource_arn])

    def add_statement(self, effect, actions, resources):
        self.statements.append({"Effect"   : effect    ,
                                "Action"   : actions   ,
                                "Resource" : resources})
        return self

    def add_statement_allow(self, actions, resources):
        return self.add_statement('Allow', actions,resources)

    def create(self):
        if self.policy_name is None:
            return {'status':'error', 'data':'policy name is None'}
        return self.iam.policy_create(self.policy_name, self.statement())

    def delete(self):
        return self.iam.policy_delete(self.policy_name)

    def exists(self):
        return self.iam.policy_exists(self.policy_name)

    def statement(self):
        return { 'Version' : self.version , 'Statement': self.statements}

