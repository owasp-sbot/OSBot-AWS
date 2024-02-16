from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

from osbot_utils.decorators.methods.cache import cache
from osbot_utils.helpers.Local_Cache import Local_Cache
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import path_combine, current_temp_folder, create_folder

from osbot_aws.aws.iam.IAM import IAM
from osbot_aws.aws.iam.IAM_Role import IAM_Role
from osbot_aws.aws.iam.STS import STS
from osbot_utils.utils.Misc import wait_for

CACHES_NAME__AWS_ROLES       = '_aws_cached_roles'

#FOLDER_NAME__CACHED_CREDENTIALS = '_aws_cached_credentials'


class IAM_Assume_Role:

    def __init__(self, role_name):
        self.role_name        = role_name
        #self.policy_statement = policy_statement
        self.cached_role      = Local_Cache(role_name, CACHES_NAME__AWS_ROLES)

    @cache
    def iam(self) -> IAM:
        return IAM()

    @cache
    def sts(self) -> STS:
        return STS()
    @cache
    def iam(self):
        return self.iam_role().iam

    @cache
    def iam_role(self) -> IAM_Role:
        return IAM_Role(role_name=self.role_name)

    def add_policy(self, service, action, resource):
        pass
    def assume_policy(self):
        return self.setup_data().get('assume_policy')

    def boto3_client(self, service_name='iam'):
        credentials = self.credentials()
        kwargs = dict(service_name          = service_name                  ,
                      aws_access_key_id     = credentials['AccessKeyId'    ],
                      aws_secret_access_key = credentials['SecretAccessKey'],
                      aws_session_token     = credentials['SessionToken'   ])
        return boto3.client(**kwargs)

    def create_credentials(self):
        self.credentials_raw()
        return self

    def create_policy_document(self, service, action, resource, effect='Allow'):
        return { "Version"  : "2012-10-17",
                 "Statement": [{"Effect" : effect               ,
                               "Action"  : f"{service}:{action}",
                               "Resource": resource             }]}

    def create_role(self, recreate=False):
        if recreate:
            self.reset()
            self.delete_role()
        #setup_data = self.setup_data()
        if self.role_exists() is False:
            self.setup_data()
            assume_policy_document = self.assume_policy()
            result__role_create    = self.iam_role().create(assume_policy_document=assume_policy_document)
            self.cached_role.set('result__role_create', result__role_create)
            self.cached_role.set('role_exists', True                 )  # todo see how to check this would having to make another Boto3 call
            self.create_credentials()

    def credentials(self, reset=False):
        if reset or self.credentials_expired():
            self.credentials_reset()

        credentials_raw = self.credentials_raw()
        if credentials_raw:
            credentials_data = credentials_raw.get('Credentials', {})
            return { 'AccessKeyId'    : credentials_data.get('AccessKeyId'    ),
                     'SecretAccessKey': credentials_data.get('SecretAccessKey'),
                     'SessionToken'   : credentials_data.get('SessionToken'   )}
        return {}

    def credentials_expiration_date(self):
        credentials_raw = self.data().get('result__credentials') or {}
        expiration  = credentials_raw.get('Credentials', {}).get('Expiration')
        if expiration:
            if type(expiration) is datetime:
                return expiration
            if type(expiration) is str:
                return  datetime.strptime(expiration, '%Y-%m-%d %H:%M:%S%z')
        return None

    def credentials_expired(self):
        expiration_time = self.credentials_expiration_date()
        if expiration_time:
            current_time = datetime.now(timezone.utc)
            return expiration_time < current_time
        return True

    def credentials_raw(self, role_session_name=None,  retries=20, delay=0.2):
        credentials_raw = self.data().get('result__credentials')
        if credentials_raw is None:
            for attempt in range(retries):
                try:
                    credentials_raw = self.sts().assume_role(role_arn=self.role_arn(), role_session_name=role_session_name)
                    self.cached_role.set('result__credentials', credentials_raw)
                    return credentials_raw
                except ClientError as e:
                    if e.response['Error']['Code'] == 'AccessDenied' and attempt < retries - 1:
                        # todo: remove this print once we confirm that this is working ok
                        print(">>>>>>>> in credentials_raw <<<<<< waiting for 0.2 seconds before retrying")
                        wait_for(delay)
                    else:
                       raise
        return credentials_raw


    def credentials_reset(self):
        self.cached_role.set('result__credentials', None)
        return self

    def data(self):
        return self.cached_role.data()

    def delete_role(self):
        self.iam_role().delete()
        self.cached_role.set('role_exists', False)             # todo see how to check this would having to make another Boto3 call
        return self


    def default_assume_policy(self, user_arn=None, service_name=None, federated=None, canonical_user=None):
        effect     = 'Allow'
        action     = 'sts:AssumeRole'
        statements = []
        def add_statement(name, target):
            if target:
                statements.append({ 'Effect': effect, 'Principal': { name: target }, 'Action': action })

        add_statement('AWS'          , user_arn      )
        add_statement('Service'      , service_name  )
        add_statement('Federated'    , federated     )
        add_statement('CanonicalUser', canonical_user)

        return { 'Version'  : '2012-10-17',
                 'Statement': statements  }

    def policies(self):
        policies = self.data().get('policies')
        if policies is None:
            policies = self.iam_role().iam.role_policies_inline(fetch_inline_policies=True)
            self.cached_role.set('policies', policies)
        return policies

    def role_arn(self):
        return self.data().get('role_arn')

    def role_exists(self):
        return self.cached_role.get('role_exists', False)


    def set_inline_policy(self, policy_name, policy_document):
        policies = self.policies()
        if (policy_name in policies) is False or policies.get(policy_name) != policy_document:
            self.iam_role().iam.role_policy_add(policy_name, policy_document)
            policies[policy_name] = policy_document
            self.cached_role.set('policies', policies)
            return True
        return False

    def setup_data(self):
        if self.cached_role.cache_exists() is False:
            role_name          = self.role_name
            caller_identity    = self.sts().caller_identity()
            current_user_arn   = caller_identity.get('Arn')
            assume_policy      = self.default_assume_policy(user_arn=current_user_arn)
            current_account_id = caller_identity.get('Account')
            current_user_id    = caller_identity.get('UserId' )

            role_arn           = f"arn:aws:iam::{current_account_id}:role/{role_name}"

            data = dict(assume_policy       = assume_policy                 ,
                        current_account_id  = current_account_id            ,
                        current_user_id     = current_user_id               ,
                        current_user_arn    = current_user_arn              ,
                        policies            = None                          ,           # setting these vars to None will trigger the reload on the first time they are used
                        result__credentials = None                          ,
                        result__role_create = None                          ,
                        role_arn            = role_arn                      ,
                        role_name           = role_name                     ,
                        role_exists         = self.iam_role().exists()      )
            self.cached_role.set_data(data)
        return self.cached_role.data()

    def reset(self):
        self.cached_role.cache_delete()
        self.setup_data()
        return self