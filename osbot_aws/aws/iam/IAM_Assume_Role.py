from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

from osbot_utils.decorators.methods.cache import cache
from osbot_utils.helpers.Local_Cache import Local_Cache
from osbot_aws.aws.iam.IAM import IAM
from osbot_aws.aws.iam.IAM_Role import IAM_Role
from osbot_aws.aws.sts.STS import STS
from osbot_utils.utils.Misc import wait_for
from osbot_utils.utils.Str import safe_str

CACHES_NAME__AWS_ROLES       = '_aws_cached_roles'

#FOLDER_NAME__CACHED_CREDENTIALS = '_aws_cached_credentials'


class IAM_Assume_Role:

    def __init__(self, role_name, policies_to_add=None):
        self.policies_to_add  = policies_to_add or []
        self.role_name        = role_name
        self.cached_role      = Local_Cache(role_name, CACHES_NAME__AWS_ROLES)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

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

    def aws__client__sts(self):
        class STS__Assume_Role(STS):
            def client(_self):
                return self.boto3_client(service_name='sts')
        return STS__Assume_Role()

    def add_policy(self, service, action, resource):
        if service and action and resource:
            policy_name = f'inline_policy_for_{safe_str(service)}_{safe_str(action)}_{safe_str(resource)}'
            policy_document = self.create_policy_document(service=service, action=action, resource=resource)
            return self.set_inline_policy(policy_name, policy_document)
        return False
    def assume_policy(self):
        return self.setup_data().get('assume_policy')

    def boto3_client(self, service_name='iam', region_name=None, retries=20):
        credentials = self.credentials(retries=retries)
        kwargs = dict(service_name          = service_name                  ,
                      aws_access_key_id     = credentials['AccessKeyId'    ],
                      aws_secret_access_key = credentials['SecretAccessKey'],
                      aws_session_token     = credentials['SessionToken'   ])
        if region_name:
            kwargs['region_name'] = region_name
        return boto3.client(**kwargs)

    def boto3_resource(self, service_name='iam', region_name=None, retries=20):
        credentials = self.credentials(retries=retries)
        kwargs = dict(service_name          = service_name                  ,
                      aws_access_key_id     = credentials['AccessKeyId'    ],
                      aws_secret_access_key = credentials['SecretAccessKey'],
                      aws_session_token     = credentials['SessionToken'   ])
        if region_name:
            kwargs['region_name'] = region_name
        return boto3.resource(**kwargs)

    def create_credentials(self, retries=30):
        self.credentials_raw(retries=retries)
        return self

    def create_policy_document(self, service, action, resource, effect='Allow'):
        return { "Version"  : "2012-10-17",
                 "Statement": [{"Effect" : effect               ,
                               "Action"  : f"{service}:{action}",
                               "Resource": resource             }]}

    def create_policies(self):
        for policy_to_add in self.policies_to_add:
            self.add_policy(**policy_to_add)

    def create_role(self, recreate=False, create_credentials=True):
        if recreate:
            self.reset()
            self.delete_role()

        if self.role_exists() is False:
            self.setup_data()
            assume_policy_document = self.assume_policy()
            result__role_create    = self.iam_role().create(assume_policy_document=assume_policy_document)
            self.cached_role.set('result__role_create', result__role_create)
            self.cached_role.set('role_exists', True                 )  # todo see how to check this would having to make another Boto3 call
            self.create_policies()
            if create_credentials:
                self.create_credentials()

    def credentials(self, reset=False, retries=30):
        if reset or self.credentials_expired():
            self.credentials_reset()

        credentials_raw = self.credentials_raw(retries=retries)
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

    def credentials_raw(self, role_session_name=None,  retries=30, delay=0.5):      # todo: capture metric for how long it takes to get the credentials
        credentials_raw = self.data().get('result__credentials')
        if credentials_raw is not None:
            return credentials_raw
        for attempt in range(retries):
            try:
                credentials_raw = self.sts().assume_role(role_arn=self.role_arn(), role_session_name=role_session_name)
                self.cached_role.set('result__credentials', credentials_raw)
                return credentials_raw
            except ClientError as e:
                if e.response['Error']['Code'] == 'AccessDenied' and attempt < retries - 1:
                    wait_for(delay)
                else:
                    print(">>>>>>>> in credentials_raw <<<<<< FAILED TO GET CREDENTIALS")
                    raise
        raise Exception(">>>>>>>> in credentials_raw <<<<<< FAILED TO GET CREDENTIALS")


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
            policies_to_add    = self.policies_to_add

            role_arn           = f"arn:aws:iam::{current_account_id}:role/{role_name}"

            data = dict(assume_policy       = assume_policy                 ,
                        current_account_id  = current_account_id            ,
                        current_user_id     = current_user_id               ,
                        current_user_arn    = current_user_arn              ,
                        policies            = None                          ,           # setting these vars to None will trigger the reload on the first time they are used
                        policies_to_add     = policies_to_add               ,
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

    def wait_for_valid_execution(self, service_name, method_name, retries=20, delay=0.2):
        for attempt in range(retries):
            try:
                target_client = self.boto3_client(service_name)
                target_method = getattr(target_client, method_name)
                return target_method()
            except Exception as e:
                print()
                print(f">> [ attempt {attempt}] in wait_for_valid_execution | waiting for {delay} seconds before retrying << ")
                print(f">>   error:{e}")
            wait_for(delay)
            self.credentials_reset()                # reset credentials before trying again