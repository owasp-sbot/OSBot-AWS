from osbot_utils.decorators.methods.cache import cache
from osbot_utils.helpers.Local_Cache import Local_Cache
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import path_combine, current_temp_folder, create_folder

from osbot_aws.aws.iam.IAM import IAM
from osbot_aws.aws.iam.IAM_Role import IAM_Role
from osbot_aws.aws.iam.STS import STS

CACHES_NAME__AWS_ROLES       = '_aws_cached_roles'

#FOLDER_NAME__CACHED_CREDENTIALS = '_aws_cached_credentials'


class IAM_Assume_Role:

    def __init__(self, role_name, policy_statement):
        self.role_name        = role_name
        self.policy_statement = policy_statement
        self.cached_role      = Local_Cache(role_name, CACHES_NAME__AWS_ROLES)

    @cache
    def iam(self) -> IAM:
        return IAM()

    def create_role(self, policy):
        return self.iam_role.create(policy)

    def role_exists(self):
        return self.iam_role.exists()

    def  current_user(self):
        return self.iam().caller_identity()

    def default_assume_policy(self, principal):
        return {'Statement': [{'Action'    : 'sts:AssumeRole'   ,
                               'Effect'   : 'Allow'             ,
                               'Principal': principal           } ]}
    @cache
    def path_cached_roles(self):
        path_folder = path_combine(current_temp_folder(), FOLDER_NAME__CACHED_ROLES)
        create_folder(path_folder)
        return path_folder

    def path_cached_credentials(self):
        return path_combine(current_temp_folder(), FOLDER_NAME__CACHED_CREDENTIALS)

    def setup(self):
        if self.cached_role.cache_exists() is False:
            caller_identity = STS().caller_identity()
            #self.cached_role.create()
            #self.cached_role.add('role_name'    , self.role_name)
            #self.cached_role.add('assume_policy', self.role_name)

        return self