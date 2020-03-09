import json
from pbx_gs_python_utils.utils.Misc     import Misc
from osbot_aws.Globals                  import Globals
from osbot_aws.apis.Session             import Session
from osbot_utils.decorators.Method_Wrappers  import cache, catch
from osbot_utils.decorators.Lists import index_by


class IAM:
    def __init__(self, user_name=None, role_name=None):
        self.user_name   = user_name
        self.role_name   = role_name

    # helpers
    @cache
    def iam(self):
        return Session().client('iam')

    @cache
    def resource(self):
        return Session().resource('iam')

    @cache
    def session(self):
        return Session().session()

    @cache
    def sts(self):
        return Session().client('sts')

    # def _index_by(self, values, index_by=None):
    #     if index_by is None:
    #         return list(values)
    #     results = {}
    #     for item in values:
    #         results[item.get(index_by)] = item
    #     return results


    # main method
    @cache
    def account_id(self, profile_name=None):
        if profile_name is not None:                            # if profile_name is set
            Globals.aws_session_profile_name = profile_name     # set it globally (since this will be used by all boto3 clients)
        return self.caller_identity().get('Account')

    @cache
    def region(self):
        return self.session().region_name
    # def assume_role(self, role_arn,role_session_name):
    #     data = self.sts().assume_role(RoleArn = role_arn, RoleSessionName=role_session_name)
    #     return data

    def caller_identity(self):
        data = self.sts().get_caller_identity()
        del data['ResponseMetadata']
        return data

    def get_data(self, method, field_id, use_paginator, **kwargs):
        paginator = self.iam().get_paginator(method)
        for page in paginator.paginate(**kwargs):
            for id in page.get(field_id):
                yield id
            if use_paginator is False:
                return

    def groups(self):
        return list(self.get_data('list_groups', 'Groups', True))

    def login_profile_create(self, password, reset_required=True):
        return self.iam().create_login_profile(UserName=self.user_name, Password=password, PasswordResetRequired=reset_required)

    def login_profile_delete(self):
        return self.iam().delete_login_profile(UserName=self.user_name)

    def policy_arn(self, policy_name, policy_path='/',account_id=None):
        if policy_name is None: return policy_name
        if account_id is None: account_id = self.account_id()
        if policy_path is None or policy_path == '/':
            return 'arn:aws:iam::{0}:policy/{1}'.format(account_id, policy_name)
        return 'arn:aws:iam::{0}:policy{1}/{2}' .format(account_id, policy_path, policy_name)

    def policy_create_version(self, policy_name, policy_document, policy_path='/', account_id=None): # todo: add support for deleting previous versions
        policy_arn = self.policy_arn(policy_name, policy_path, account_id)
        if type(policy_document) is not str:
            policy_document = json.dumps(policy_document)
        data = self.iam().create_policy_version(PolicyArn=policy_arn, PolicyDocument=policy_document,SetAsDefault=True).get('Policy')
        return {'status': 'ok', 'policy_name': policy_name, 'policy_arn': policy_arn, 'data': data}

    def policy_create(self, policy_name, policy_document, policy_path='/', account_id=None, delete_before_create=False):
        policy_arn = self.policy_arn(policy_name, policy_path,account_id)
        if delete_before_create:
            self.policy_delete(policy_arn)
        if self.policy_exists(policy_arn) is False:
            if type(policy_document) is not str:
                policy_document = json.dumps(policy_document)
            try:
                data       = self.iam().create_policy(PolicyName=policy_name, PolicyDocument=policy_document).get('Policy')
                policy_arn = data.get('Arn')
                return {'status': 'ok'     , 'policy_name': policy_name, 'policy_arn': policy_arn                  , 'data': data                     }
            except Exception as error:
                return {'status': 'error'  , 'policy_name': policy_name, 'policy_arn': None                        , 'data': '{0}'.format(error)      }
        return {        'status': 'warning', 'policy_name': policy_name, 'policy_arn': policy_arn                  , 'data': 'policy already existed' }

    def policy_delete(self, policy_arn):
        if self.policy_exists(policy_arn) is False: return False
        self.policy_detach_roles(policy_arn)
        self.iam().delete_policy(PolicyArn= policy_arn)
        return self.policy_exists(policy_arn) is False

    def policy_delete_by_name(self, policy_name, policy_path='/',account_id=None):
        policy_arn = self.policy_arn(policy_name,policy_path,account_id)
        if self.policy_exists(policy_arn) is False: return False
        self.iam().delete_policy(PolicyArn= policy_arn)
        return self.policy_exists(policy_arn) is False

    def policy_info(self, policy_arn):
        try:
            return self.iam().get_policy(PolicyArn=policy_arn).get('Policy')
        except:
            return None

    def policy_details(self, policy_arn):
        try:
            policy_info    = self.policy_info(policy_arn)
            if policy_info:
                policy_arn     = policy_info.get('Arn')
                version_id     = policy_info.get('DefaultVersionId')
                policy_version = self.iam().get_policy_version(PolicyArn=policy_arn, VersionId=version_id).get('PolicyVersion')
                return {'policy_arn': policy_arn, 'policy_name': policy_info.get('PolicyName'), 'policy_info' : policy_info, 'policy_version': policy_version}
        except:
            return None

    def policy_detach_roles(self,policy_arn):
        policy_roles = self.iam().list_entities_for_policy(PolicyArn=policy_arn).get('PolicyRoles')
        for role in policy_roles:
            IAM(role_name=role.get('RoleName')).role_policy_detach(policy_arn)
        return self

    def policy_statement(self, policy_arn):
        policy_details = self.policy_details(policy_arn)
        if policy_details:
            return policy_details.get('policy_version').get('Document').get('Statement')

    def policy_exists(self, policy_arn):
        return self.policy_info(policy_arn) is not None

    def policy_exists_by_name(self, policy_name, policy_path='/', account_id=None):
        calculated_policy_arn = self.policy_arn(policy_name, policy_path, account_id)   # since there doesn't seem to be a way to search for a policy by name
        return self.policy_info(calculated_policy_arn) is not None

    @index_by
    def policies(self):
        return list(self.get_data('list_policies', 'Policies', True))

    def policies_delete(self, policies_names):
        for policy_name in policies_names:
            self.policy_delete(policy_name)

    def role_arn(self):
        return Misc.get_value(self.role_info(), 'Arn')

    def role_exists(self):
        return self.role_info() is not None

    def role_info(self):
        try:
            return self.iam().get_role(RoleName=self.role_name).get('Role')
        except:
            return None

    def role_create(self, policy_document):
        if type(policy_document) is not str:
            policy_document = json.dumps(policy_document)
        if self.role_exists() is False:
            return self.iam().create_role(RoleName=self.role_name, AssumeRolePolicyDocument=policy_document).get('Role')

    def role_delete(self):
        if self.role_exists() is False: return False                # make sure it exists
        self.role_policies_detach_and_delete()                      # delete all associated policies
        self.iam().delete_role(RoleName=self.role_name)
        return self.role_exists() is False

    def role_policies_detach_and_delete(self):
        policies_arns = self.role_policies().values()
        self.role_policies_detach(policies_arns)
        self.policies_delete     (policies_arns)

    def role_policy_attach(self,policy_arn):
        return self.iam().attach_role_policy(RoleName=self.role_name, PolicyArn=policy_arn)

    def role_policy_detach(self, policy_arn):
        self.iam().detach_role_policy(RoleName=self.role_name, PolicyArn=policy_arn)

    def role_policies_detach(self, policies_arn):
        for policy_arn in policies_arn:
            self.role_policy_detach(policy_arn)


    def role_policies_attach(self, policies_arn):
        for policy_arn in policies_arn:
            self.role_policy_attach(policy_arn)

    @catch
    def role_policies(self):
        policies = {}
        if self.role_name:
            for item in self.get_data('list_attached_role_policies', 'AttachedPolicies', True, RoleName=self.role_name):
                policies[item.get('PolicyName')] = item.get('PolicyArn')
        return policies

    def role_policies_statements(self, just_statements = False):
        if just_statements:
            statements = []
            for items in self.role_policies_statements().values():
                statements.extend(items)
            return statements

        policy_statements = {}
        for policy_name, policy_arn in self.role_policies().items():
            policy_statements[policy_name] = self.policy_statement(policy_arn)
        return policy_statements


    @index_by
    def roles(self):
        return list(self.get_data('list_roles', 'Roles', True))

    @index_by
    def users(self):
        return self.get_data('list_users', 'Users', True)

    def user_attach_policy(self, policy_arn):
        return self.iam().attach_user_policy(UserName=self.user_name, PolicyArn=policy_arn)

    def user_exists(self):
        return self.user_info().get('error') is not None

    @catch
    def user_info(self):
        return self.iam().get_user(UserName=self.user_name).get('User')

    def user_create(self):
        if self.user_exists() is False:
            return self.iam().create_user(UserName=self.user_name).get('User')
        return self.user_info()

    def user_delete(self):
        if self.user_exists() is False: return False
        self.login_profile_delete()
        self.iam().delete_user(UserName=self.user_name)
        return self.user_exists() is False

    def set_account_id(self, value): self._account_id = value ;return self
    def set_user_name (self, value): self.user_name   = value ;return self
    def set_role_name (self, value): self.role_name   = value; return self
