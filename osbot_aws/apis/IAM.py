import json

import boto3

class IAM:

    def __init__(self, user_name=None, role_name=None):
        self.iam       = boto3.client('iam')
        self.user_name = user_name
        self.role_name = role_name

    def get_data(self, method, field_id, use_paginator, **kwargs):
        paginator = self.iam.get_paginator(method)
        for page in paginator.paginate(**kwargs):
            for id in page.get(field_id):
                yield id
            if use_paginator is False:
                return

    def account_id(self):
        sts = boto3.client('sts')
        account_id = sts.get_caller_identity()
        return account_id.get('Account')

    def groups(self):
        return list(self.get_data('list_groups', 'Groups', True))

    def policy_arn(self, policy_name):
        return 'arn:aws:iam::{0}:policy/{1}'.format(self.account_id(), policy_name)

    def policy_create(self, policy_name, policy_document):
        if self.policy_exists(policy_name) is False:
            if type(policy_document) is not str:
                policy_document = json.dumps(policy_document)
            return self.iam.create_policy(PolicyName=policy_name, PolicyDocument=policy_document)

    def policy_delete(self, policy_name):
        if self.policy_exists(policy_name) is False: return False
        self.iam.delete_policy(PolicyArn= self.policy_arn(policy_name))
        return self.policy_exists(policy_name) is False

    def policy_info(self,policy_name):
        try:
            return self.iam.get_policy(PolicyArn=self.policy_arn(policy_name)).get('Policy')
        except:
            return None

    def policy_exists(self, policy_name):
        return self.policy_info(policy_name) is not None

    def policies(self):
        return list(self.get_data('list_policies', 'Policies', True))

    def role_exists(self):
        return self.role_info() is not None

    def role_info(self):
        try:
            return self.iam.get_role(RoleName=self.role_name).get('Role')
        except:
            return None

    def role_create(self, policy_document):
        if type(policy_document) is not str:
            policy_document = json.dumps(policy_document)
        if self.role_exists() is False:
            return self.iam.create_role(RoleName=self.role_name, AssumeRolePolicyDocument=policy_document).get('Role')

    def role_delete(self):
        if self.role_exists() is False: return False
        self.role_policies_detach(list(self.role_policies().values()))
        self.iam.delete_role(RoleName=self.role_name)
        return self.role_exists() is False


    def role_policies_detach(self, policies_arn):
        if type(policies_arn) is list:
            for policy_arn in policies_arn:
                self.iam.detach_role_policy(RoleName=self.role_name, PolicyArn=policy_arn)
        else:
            self.iam.detach_role_policy(RoleName=self.role_name, PolicyArn=policies_arn)

    def role_policies_attach(self, policies_arn):
        if type(policies_arn) is list:
            for policy_arn in policies_arn:
                self.iam.attach_role_policy(RoleName=self.role_name, PolicyArn=policy_arn)
        else:
            self.iam.attach_role_policy(RoleName=self.role_name, PolicyArn=policies_arn)

    def role_policies(self):
        policies = {}
        for item in self.get_data('list_attached_role_policies', 'AttachedPolicies', True, RoleName=self.role_name):
            policies[item.get('PolicyName')] = item.get('PolicyArn')
        return policies

    def roles(self):
        return list(self.get_data('list_roles', 'Roles', True))

    def users(self):
        return list(self.get_data('list_users', 'Users', True))

    def user_exists(self):
        return self.user_info() is not None

    def user_info(self):
        try:
            return self.iam.get_user(UserName=self.user_name).get('User')
        except:
            return None

    def user_create(self):
        if self.user_exists() is False:
            return self.iam.create_user(UserName=self.user_name).get('User')

    def user_delete(self):
        if self.user_exists() is False: return False
        self.iam.delete_user(UserName=self.user_name)
        return self.user_exists() is False

    def set_user_name(self,user_name):
        self.user_name = user_name
        return self

    def set_role_name(self, role_name):
        self.role_name = role_name
        return self
