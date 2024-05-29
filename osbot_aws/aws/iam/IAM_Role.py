from osbot_utils.utils.Misc         import random_string
from osbot_utils.utils.Status import status_error, status_ok

from osbot_aws.AWS_Config           import AWS_Config
from osbot_aws.aws.iam.IAM          import IAM
from osbot_aws.aws.iam.IAM_Policy   import IAM_Policy


class IAM_Role:
    def __init__(self,role_name=None, role_arn=None):
        if role_arn:
            self.role_name = role_arn.split('/')[-1]
        else:
            self.role_name  = role_name or f"osbot_temp_role_{random_string()}"
        self.iam        = IAM(role_name=self.role_name)

    def add_policy_for__lambda(self):
        temp_policy_name = 'policy_{0}'.format(self.role_name)
        cloud_watch_arn  = f'arn:aws:logs:{AWS_Config().aws_session_region_name()}:{AWS_Config().aws_session_account_id()}:log-group:/aws/lambda/*'
        iam_policy       = IAM_Policy(temp_policy_name)
        policy_arn       = iam_policy.add_cloud_watch(cloud_watch_arn).create().get('policy_arn')
        self.iam.role_policy_attach(policy_arn)
        return policy_arn

    def arn(self):
        return self.iam.role_arn()

    def attach_policy(self, policy_name, policy_document):
        self.delete_policy(policy_name= policy_name)
        result_create = self.iam.policy_create(policy_name=policy_name, policy_document=policy_document)
        policy_arn = result_create.get('policy_arn')
        self.iam.role_policy_attach(policy_arn=policy_arn)
        return policy_arn

    def create(self, assume_policy_document, skip_if_exists=True):
        try:
            role_info = self.iam.role_create(assume_policy_document=assume_policy_document, skip_if_exists=skip_if_exists)
            return status_ok(data    = role_info                                         ,
                             message = f'user created (skip_if_exists: {skip_if_exists})')
        except Exception as error:
            return status_error(data    = dict(assume_policy_document=assume_policy_document)                         ,
                                error   = error                                                                       ,
                                message = f'error creating role with assume_policy_document: {assume_policy_document}')

        #return self.exists()

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

    def create_instance_profile(self):
        return self.iam.role_create_instance_profile(role_name=self.role_name).get('InstanceProfile')

    def add_to_instance_profile(self):
        return self.iam.role_add_to_instance_profile(instance_profile_name=self.role_name, role_name=self.role_name) # it seems that the convension is to use the same for both

    def delete(self):
        return self.iam.role_delete()

    def delete_policy(self, policy_arn=None, policy_name=None):
        return self.iam.policy_delete(policy_arn=policy_arn, policy_name=policy_name)

    def exists(self):
        return self.iam.role_exists()

    def info(self):
        return self.iam.role_info()

    def not_exists(self):
        return self.iam.role_not_exists()

    def policies(self):
        for policy_name, policy_statements in self.policies_statements().items():
            yield IAM_Policy(policy_name, policy_statements)


    def policies_statements(self):
        return self.iam.role_policies_statements()