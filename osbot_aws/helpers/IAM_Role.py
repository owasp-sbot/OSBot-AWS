from pbx_gs_python_utils.utils.Dev import Dev

from osbot_aws.apis.IAM import IAM
from osbot_aws.helpers.IAM_Policy import IAM_Policy
from osbot_aws.Globals import Globals


class IAM_Role:
    def __init__(self,role_name):
        self.role_name  = role_name
        self.iam        = IAM(role_name=self.role_name)
        self.role_arn   = None
        self.policy_arn = None

    def add_policy_for__lambda(self):
        temp_policy_name = 'policy_{0}'.format(self.role_name)
        cloud_watch_arn  = f'arn:aws:logs:{Globals.aws_session_region_name}:{Globals.aws_session_account_id}:log-group:/aws/lambda/*'
        iam_policy       = IAM_Policy(temp_policy_name)
        self.policy_arn  = iam_policy.add_cloud_watch(cloud_watch_arn).create().get('policy_arn')
        self.iam.role_policy_attach(self.policy_arn)
        return self


    def create_for__lambda(self):
        result = self.create_for_service('lambda.amazonaws.com')
        if result.get('status') == 'ok':
            self.add_policy_for__lambda()
        return result

    def create_for__code_build(self):
        return self.create_for_service('codebuild.amazonaws.com')

    def create_for_service(self,service):
        role_arn =  self.iam.role_arn()
        if role_arn:
            return {'status':'warning', 'data': 'role already exists', 'role_name': self.iam.role_name , 'role_arn': role_arn}
        else:
            policy_document = {'Statement': [{'Action': 'sts:AssumeRole',
                                              'Effect': 'Allow',
                                              'Principal': {'Service': service}}]}
            data = self.iam.role_create(policy_document)
            return {'status': 'ok', 'data': data, 'role_name': self.iam.role_name, 'role_arn': data.get('Arn') }
