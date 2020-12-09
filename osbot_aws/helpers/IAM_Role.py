from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.apis.IAM import IAM
from osbot_aws.helpers.IAM_Policy import IAM_Policy



class IAM_Role:
    def __init__(self,role_name):
        self.role_name  = role_name
        self.iam        = IAM(role_name=self.role_name)
        self.role_arn   = None
        self.policy_arn = None

    def add_policy_for__lambda(self):
        temp_policy_name = 'policy_{0}'.format(self.role_name)
        cloud_watch_arn  = f'arn:aws:logs:{AWS_Config().aws_session_region_name()}:{AWS_Config().aws_session_account_id()}:log-group:/aws/lambda/*'
        iam_policy       = IAM_Policy(temp_policy_name)
        self.policy_arn  = iam_policy.add_cloud_watch(cloud_watch_arn).create().get('policy_arn')
        self.iam.role_policy_attach(self.policy_arn)
        return self


    def create_for__lambda(self):
        result = self.create_for_service__assume_role('lambda.amazonaws.com')
        if result.get('status') == 'ok':
            self.add_policy_for__lambda()
        return result

    def create_for__code_build(self):
        return self.create_for_service__assume_role('codebuild.amazonaws.com')

    def create_for_service__assume_role(self, service):
        statement = {'Action': 'sts:AssumeRole',
                      'Effect': 'Allow',
                      'Principal': {'Service': service}}
        return self.create_from_statement(statement)

    def create_for_service(self, service, statement):
        statement['Principal'] = {'Service': service}
        return self.create_from_statement(statement)

    def create_for_service_with_policies(self, service, policies, project_name, recreate_policy = False):
        role          = self.create_for_service__assume_role(service)
        role_arn      = role.get('role_arn')
        policies_arns = self.iam.policies_create(policies, project_name, recreate_policy)
        self.iam.role_policies_attach(policies_arns)
        return { "role_arn":  role_arn, "policies_arns" :policies_arns }

    def create_from_statement(self, statement):
        return self.create_from_statements([statement])

    def create_from_statements(self, statement):
        role_arn =  self.iam.role_arn()
        if role_arn:
            return {'status':'warning', 'data': 'role already exists', 'role_name': self.iam.role_name , 'role_arn': role_arn}
        else:
            policy_document = {'Statement': statement}
            data = self.iam.role_create(policy_document)
            return {'status': 'ok', 'data': data, 'role_name': self.iam.role_name, 'role_arn': data.get('Arn') }

