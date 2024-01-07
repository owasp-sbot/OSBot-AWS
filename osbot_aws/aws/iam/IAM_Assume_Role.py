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
    def iam_role(self) -> IAM_Role:
        return IAM_Role(role_name=self.role_name)

    def assume_policy(self):
        return self.setup_data().get('assume_policy')

    def create_role(self):
        #setup_data = self.setup_data()
        if self.role_exists() is False:
            assume_policy_document = self.assume_policy()
            result = self.iam_role().create(assume_policy_document=assume_policy_document)
            #pprint(result)

        #return setup_data
        #return self.iam_role().create(policy)

    def role_exists(self):
        return self.setup_data().get('role_exists', False)

    def default_assume_policy(self, principal):
        return {'Statement': [{'Action'    : 'sts:AssumeRole'   ,
                               'Effect'   : 'Allow'             ,
                               'Principal': principal           } ]}
    # @cache
    # def path_cached_roles(self):
    #     path_folder = path_combine(current_temp_folder(), FOLDER_NAME__CACHED_ROLES)
    #     create_folder(path_folder)
    #     return path_folder
    #
    # def path_cached_credentials(self):
    #     return path_combine(current_temp_folder(), FOLDER_NAME__CACHED_CREDENTIALS)

    def setup_data(self):
        if self.cached_role.cache_exists() is False:
            caller_identity  = self.sts().caller_identity()
            current_user_arn = caller_identity.get('Arn')
            assume_policy    = self.default_assume_policy(current_user_arn)

            data = dict(assume_policy      = assume_policy                 ,
                        current_account_id = caller_identity.get('Account'),
                        current_user_id    = caller_identity.get('UserId' ),
                        current_user_arn   = current_user_arn              ,
                        role_name          = self.role_name                ,
                        role_exists        = self.iam_role().exists()      )
            self.cached_role.set_data(data)
        return self.cached_role.data()