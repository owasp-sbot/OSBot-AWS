import json
from functools import cache

import boto3

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Objects import get_value

from osbot_utils.decorators.methods.cache_on_self   import cache_on_self
from osbot_utils.decorators.lists.group_by          import group_by
from osbot_utils.decorators.lists.index_by          import index_by
from osbot_utils.decorators.methods.catch           import catch
from osbot_utils.decorators.methods.remove_return_value import remove_return_value
from osbot_utils.testing.Duration import Duration
from osbot_utils.utils.Json import json_to_str, from_json_str
from osbot_utils.utils.Misc import random_string, wait
from osbot_utils.utils.Status import status_ok, status_error

from osbot_aws.apis.Session                         import Session
from osbot_aws.aws.sts.STS import STS


class IAM:

    # todo: remove user_name and role_name from here
    def __init__(self, user_name=None, role_name=None):
        self.user_name   = user_name                        # todo: refactor this variable into the method's definition (to make it consistent with the other APIs)
        self.role_name   = role_name                        #       this will be a bit of a breaking change to code that uses this class for role management

    # helpers
    @cache
    def client(self):                                          # rename to client
        return Session().client('iam')

    @cache
    def resource(self):
        return Session().resource('iam')

    @cache
    def session(self):
        return Session().session()

    @cache
    def sts(self):
        return STS()


    # main method
    #todo: refactor with better wait solution
    def access_key__wait_until_key_is_working(self, access_key, wait_for=0.5 , wait_count=20, success_count=5):
        """
        Wait until the access key is working. When testing this there a number of cases where
        access_key__is_key_working would return False after a True one (which means that AWS was still not fully syncronised (see https://aws.amazon.com/iam/faqs/ and https://stackoverflow.com/questions/20156043/how-long-should-i-wait-after-applying-an-aws-iam-policy-before-it-is-valid)
        :param access_key:
        :param wait_count:
        :param success_count:  if still seeing some false positives include the default value (set to 5)
        :return:
        """
        if success_count < 1:                                                   # make sure this value is not below 1
            success_count = 1
        status    = False
        key_is_ok = 0
        with Duration() as duration:
            for i in range(1,wait_count):
                if self.access_key__is_key_working(access_key) is True:         # the get_caller_identity takes about 500ms to execute
                    key_is_ok += 1                                              # increment key_is_ok
                    if key_is_ok == success_count:                              # only after success_count matches, we can reliable say that key is good
                        status = True
                        break
                    continue
                wait(wait_for)
        if status:
            message = f'access key ok: during {duration.seconds()} seconds, confirmed {key_is_ok} times that the key is working'
            return status_ok(message=message)
        else:
            message = f'access not working ok: after {duration.seconds()} seconds, was only able to confirm {key_is_ok} times that the key was working'
            return status_error(message=message)

    def access_key__wait_until_key_is_not_working(self, access_key, wait_count=100, success_count=30):
        """
        waits until the access key is not working anymore
        note: I couldn't get this to provide a consistent result with values smaller than 30
        :param access_key:
        :param wait_count:
        :param success_count:
        :return:
        """

        for i in range(1,wait_count):
            if self.access_key__is_key_working(access_key) is False:        # the get_caller_identity takes about 500ms to execute
                success_count -= 1
                if success_count == 0:
                    print(f'waited {i} times - before confirming key is not working anymore')
                    return True
        return False

    def access_key__is_key_working(self, access_key):       # todo refactor to Sessions class
        aws_access_key_id     = access_key.get('AccessKeyId')
        aws_secret_access_key = access_key.get('SecretAccessKey')
        try:
            session = boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
            session.client('sts').get_caller_identity()
            return True
        except Exception as error:
            assert error.__str__() == 'An error occurred (InvalidClientTokenId) when calling the GetCallerIdentity operation: The security token included in the request is invalid.'
            return False

    @group_by
    @index_by
    def access_keys(self):
        return self.client().list_access_keys().get('AccessKeyMetadata')

    @cache
    def account_id(self):
        return self.sts().current_account_id()

    def check_aws_security_tokens(self):
        try:
            identity = self.caller_identity()
            return {'status': "Ok", 'error': None, "data": identity}
        except Exception as error:
            return { 'status': "Error", 'error':error, "data":None}


    @cache_on_self
    def region(self):
        return self.session().region_name

    @remove_return_value('ResponseMetadata')
    def caller_identity(self):
        return self.sts().caller_identity()

    def get_data(self, method, field_id, use_paginator, **kwargs):
        paginator = self.client().get_paginator(method)
        for page in paginator.paginate(**kwargs):
            for id in page.get(field_id):
                yield id
            if use_paginator is False:
                return

    def groups(self):
        return self.get_data('list_groups', 'Groups', True)

    @catch
    def login_profile(self):
        return self.client().get_login_profile(UserName=self.user_name)

    def login_profile_create(self, password, reset_required=True):
        return self.client().create_login_profile(UserName=self.user_name, Password=password, PasswordResetRequired=reset_required)

    def login_profile_delete(self):
        if self.login_profile_exists():
            self.client().delete_login_profile(UserName=self.user_name)

    def login_profile_exists(self):
        return self.login_profile().get('error') is None

    def policy_arn(self, policy_name, policy_path='/',account_id=None):
        if policy_name is None: return policy_name
        if account_id  is None: account_id = self.account_id()
        if policy_path is None or policy_path == '/':
            return f'arn:aws:iam::{account_id}:policy/{policy_name}'
        return f'arn:aws:iam::{account_id}:policy{policy_path}/{policy_name}'

    def policy_create_version(self, policy_name, policy_document, policy_path='/', account_id=None): # todo: add support for deleting previous versions
        policy_arn = self.policy_arn(policy_name, policy_path, account_id)
        if type(policy_document) is not str:
            policy_document = json.dumps(policy_document)
        data = self.client().create_policy_version(PolicyArn=policy_arn, PolicyDocument=policy_document, SetAsDefault=True).get('Policy')
        return {'status': 'ok', 'policy_name': policy_name, 'policy_arn': policy_arn, 'data': data}

    def policies_create(self, policies, project_name=None, recreate_policy=False):
        policies_arns           = []
        existing_policies       = self.role_policies()
        existing_policies_names = list(existing_policies.keys())
        project_name            = project_name or random_string()
        for base_name, policy in policies.items():
            policy_name = "{0}_{1}".format(base_name, project_name)
            if policy_name in existing_policies_names:
                existing_policy_arn = existing_policies[policy_name]
                if recreate_policy:
                    self.policy_delete(existing_policy_arn)
                else:
                    policies_arns.append(existing_policy_arn)
                    continue
            result = self.policy_create(policy_name, policy)
            policies_arns.append(result.get('policy_arn'))
        return policies_arns

    def policy_create(self, policy_name, policy_document, policy_path='/', account_id=None, delete_before_create=False):
        policy_arn = self.policy_arn(policy_name, policy_path,account_id)
        if delete_before_create:
            self.policy_delete(policy_arn)
        if self.policy_exists(policy_arn) is False:
            if type(policy_document) is not str:
                policy_document = json.dumps(policy_document)
            try:
                data       = self.client().create_policy(PolicyName=policy_name, PolicyDocument=policy_document).get('Policy')
                policy_arn = data.get('Arn')
                return {'status': 'ok'     , 'policy_name': policy_name, 'policy_arn': policy_arn                  , 'data': data                     }
            except Exception as error:
                return {'status': 'error'  , 'policy_name': policy_name, 'policy_arn': None                        , 'data': '{0}'.format(error)      }
        return {        'status': 'warning', 'policy_name': policy_name, 'policy_arn': policy_arn                  , 'data': 'policy already existed' }

    def policy_delete(self, policy_arn=None, policy_name=None):
        if policy_arn:
            if self.policy_exists(policy_arn) is False: return False
        elif policy_name:
            role_policies = self.role_policies()
            if policy_name in role_policies:
                policy_arn=role_policies.get(policy_name)
            else:
                return False
        else:
            return False
        self.policy_detach_roles(policy_arn)
        self.client().delete_policy(PolicyArn= policy_arn)
        return self.policy_exists(policy_arn) is False

    def policy_delete_by_name(self, policy_name, policy_path='/',account_id=None):
        policy_arn = self.policy_arn(policy_name,policy_path,account_id)
        if self.policy_exists(policy_arn) is False: return False
        self.client().delete_policy(PolicyArn= policy_arn)
        return self.policy_exists(policy_arn) is False

    def policy_info(self, policy_arn):
        try:
            return self.client().get_policy(PolicyArn=policy_arn).get('Policy')
        except:
            return None

    def policy_inline_delete(self, policy_name):
        return self.client().delete_role_policy(RoleName=self.role_name, PolicyName=policy_name)

    def policy_details(self, policy_arn):
        try:
            policy_info    = self.policy_info(policy_arn)
            if policy_info:
                policy_arn     = policy_info.get('Arn')
                version_id     = policy_info.get('DefaultVersionId')
                policy_version = self.client().get_policy_version(PolicyArn=policy_arn, VersionId=version_id).get('PolicyVersion')
                return {'policy_arn': policy_arn, 'policy_name': policy_info.get('PolicyName'), 'policy_info' : policy_info, 'policy_version': policy_version}
        except:
            return None

    def policy_detach_roles(self,policy_arn):
        policy_roles = self.client().list_entities_for_policy(PolicyArn=policy_arn).get('PolicyRoles')
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

    def policy_not_exists(self, policy_arn):
        return self.policy_exists(policy_arn) is False

    @index_by
    def policies(self):
        return self.get_data('list_policies', 'Policies', True)

    def policies_delete(self, policies_names):
        for policy_name in policies_names:
            self.policy_delete(policy_name)

    def role_arn(self):
        return get_value(self.role_info(), 'Arn')

    def role_assume_policy(self):
        return self.role_info().get('AssumeRolePolicyDocument')

    def role_assume_policy_update(self, policy_document):
        if type(policy_document) is not str:
            policy_document = json_to_str(policy_document)
        return self.client().update_assume_role_policy(RoleName=self.role_name, PolicyDocument=policy_document)

    def role_exists(self):
        return self.role_info() is not None

    def role_info(self):
        try:
            return self.client().get_role(RoleName=self.role_name).get('Role')
        except:
            return None

    def role_create(self, assume_policy_document, skip_if_exists=True):
        role_info = self.role_info()
        if role_info:
            if skip_if_exists:
                return role_info                     # todo: confirm that the values we get from self.role_info() are compatible with the values in .get('Role') (below)
            else:
                self.role_delete(check_exists=False)
        if type(assume_policy_document) is not str:
            assume_policy_document = json.dumps(assume_policy_document)
        result = self.client().create_role(RoleName=self.role_name, AssumeRolePolicyDocument=assume_policy_document)
        if result:
            return result.get('Role')

    def role_delete(self, check_exists=True):
        if check_exists and self.role_exists() is False:
            return False                                            # make sure it exists
        self.role_policies_detach_and_delete()                      # delete all associated policies
        result = self.client().delete_role(RoleName=self.role_name)
        if result:
            return result.get('ResponseMetadata',{}).get('HTTPStatusCode') == 200
        return False

    def role_create_instance_profile(self, role_name):
        return self.client().create_instance_profile(InstanceProfileName=role_name)

    def role_add_to_instance_profile(self, role_name, instance_profile_name):
        return self.client().add_role_to_instance_profile(InstanceProfileName = instance_profile_name,
                                                          RoleName            = role_name            )
    def role_not_exists(self):
        return self.role_exists() is False

    def role_policies_detach_and_delete(self):
        attached_policies_arns = self.role_policies_attached().values()
        self.role_policies_detach(attached_policies_arns)
        self.role_policies_delete()
        #self.policies_delete     (policies_arns)       # was a BUG, we shouldn't be deleting top level policies here

    def role_policy_add(self, policy_name, policy_document):
        if type(policy_document) is not str:
            policy_document = json_to_str(policy_document)
        return self.client().put_role_policy(RoleName=self.role_name,PolicyName=policy_name,PolicyDocument=policy_document)

    def role_policy_attach(self,policy_arn):
        return self.client().attach_role_policy(RoleName=self.role_name, PolicyArn=policy_arn)

    def role_policy_detach(self, policy_arn):
        self.client().detach_role_policy(RoleName=self.role_name, PolicyArn=policy_arn)

    def role_policies_detach(self, policies_arn):
        for policy_arn in policies_arn:
            self.role_policy_detach(policy_arn)
        return self

    def role_policies_delete(self):
        inline_policies = self.client().list_role_policies(RoleName=self.role_name)
        for policy_name in inline_policies['PolicyNames']:
            self.client().delete_role_policy(RoleName=self.role_name, PolicyName=policy_name)
        return self


    def role_policies_attach(self, policies_arn):
        for policy_arn in policies_arn:
            self.role_policy_attach(policy_arn)
        return self

    @index_by
    def role_policies(self):
        policies_attached = self.role_policies_attached()
        policies_inline   = self.role_policies_inline  ()
        return {**policies_attached, **policies_inline}

    @index_by
    def role_policies_attached(self):
        policies = {}
        if self.role_name:
            policies_attached = self.get_data('list_attached_role_policies', 'AttachedPolicies', True, RoleName=self.role_name)
            if policies_attached:
                for item in policies_attached:
                    policies[item.get('PolicyName')] = item.get('PolicyArn')
        return policies

    @index_by
    def role_policies_inline(self, fetch_inline_policies=False):
        policies = {}
        if self.role_name:
            policies_inline = self.get_data('list_role_policies', 'PolicyNames', True, RoleName=self.role_name)
            if policies_inline:
                for item in policies_inline:
                    #policies[item.get('PolicyName')] = item.get('PolicyArn')
                    policies[item] = {'PolicyName': item}                           # list_role_policies only returns an arroy of names, not the actual policy
        if fetch_inline_policies:
            for policy_name in policies.keys():

                policy_document = self.client().get_role_policy(RoleName=self.role_name, PolicyName=policy_name)
                policies[policy_name] = policy_document.get('PolicyDocument')
                #print(f"Policy Name: {policy_name}")
                #print("Policy Document:", policy_document['PolicyDocument'])

        return policies

    def role_policies_statements(self, just_statements = False):
        if just_statements:
            statements = []
            for items in self.role_policies_statements(just_statements=False).values():     # todo: find a better way to do this, this pattern looks and feels weird
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

    def users_by_username(self):
        return self.users(index_by='UserName')

    def user_access_key_create(self, wait_for_key_working=False):
        access_key = self.client().create_access_key(UserName=self.user_name).get('AccessKey')
        if wait_for_key_working:
            result = self.access_key__wait_until_key_is_working(access_key)
            if result.get('status') == 'ok':
                return None
        return access_key

    def user_access_key_delete(self, access_key_id):
        return self.client().delete_access_key(UserName=self.user_name, AccessKeyId=access_key_id)

    @index_by
    def user_access_keys(self):
        return self.client().list_access_keys(UserName=self.user_name).get('AccessKeyMetadata')

    def user_access_keys_delete_all(self):
        for access_key in self.user_access_keys():
            self.user_access_key_delete(access_key.get('AccessKeyId'))
        return len(self.user_access_keys()) == 0

    def user_attach_policy(self, policy_arn):
        return self.client().attach_user_policy(UserName=self.user_name, PolicyArn=policy_arn)

    def user_exists(self):
        return self.user_info().get('error') is None

    @catch
    def user_info(self):
        return self.client().get_user(UserName=self.user_name).get('User')

    def user_create(self):
        if self.user_exists() is False:
            return self.client().create_user(UserName=self.user_name).get('User')
        return self.user_info()

    def user_delete(self):
        if self.user_exists() is False: return False            # return False if user doesn't exist
        self.login_profile_delete()                             # delete user's profile
        self.user_access_keys_delete_all()                      # delete user's access keys
        self.client().delete_user(UserName=self.user_name)         # delete user
        return self.user_exists() is False                      # return True if user doesn't exist any more (which it shouldn't)

    def user_polices(self):
        return self.client().list_user_policies(UserName=self.user_name)

    def set_user_name (self, value): self.user_name   = value ;return self
    def set_role_name (self, value): self.role_name   = value; return self

    def wait_for_policy(self, policy_name, delay=None, max_attempts=None):
        waiter_name = 'policy_exists'
        arg_name    = 'PolicyArn'
        return self.wait_for_waiter(waiter_name, arg_name, policy_name, delay, max_attempts)

    def wait_for_role(self, role_name, delay=None, max_attempts=None):
        waiter_name = 'role_exists'
        arg_name    = 'RoleName'
        return self.wait_for_waiter(waiter_name, arg_name, role_name, delay, max_attempts)

    def wait_for_waiter(self, waiter_name, arg_name, arg_value, delay=None, max_attempts=None):
        kwargs = {
            arg_name : arg_value
        }
        kwargs['WaiterConfig'] = {
            'Delay'      : delay        or 1,               # 1  is default boto3 value for Delay
            'MaxAttempts': max_attempts or 20               # 20 is default boto3 value for Delay
        }

        waiter = self.client().get_waiter(waiter_name)
        waiter.wait(**kwargs)
        return waiter

