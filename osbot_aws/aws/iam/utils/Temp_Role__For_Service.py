from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.aws.iam.IAM_Assume_Role              import IAM_Assume_Role
from osbot_aws.aws.iam.utils.Temp_Role__For_Service__Config import Temp_Role__For_Service__Config
from osbot_utils.base_classes.Type_Safe             import Type_Safe
from osbot_utils.decorators.methods.cache_on_self   import cache_on_self
from osbot_utils.utils.Env                          import load_dotenv



class Temp_Role__For_Service(Type_Safe):
    aws_config                    : AWS_Config
    _temp_role_config             : Temp_Role__For_Service__Config

    def _iam_assume_role(self):
        role_data         = self._temp_role_config.data()
        service           = role_data.boto3_service_name
        action            = role_data.action
        resource          = role_data.resource
        role_name         = role_data.role_name
        required_services = role_data.required_services

        policies_to_add = []
        for temp_role__service in required_services:
            policies_to_add.append(dict(service=temp_role__service, action=action, resource=resource))

        iam_assume_role = IAM_Assume_Role(role_name=role_name, policies_to_add=policies_to_add)
        return iam_assume_role

    def _create_role_and_credentials(self):
        role_recreate = self._temp_role_config.recreate
        self._iam_assume_role().create_role(recreate=role_recreate)
        return self

    def _config_role_to_create(self, boto3_service_name, required_services):
        self._temp_role_config.boto3_service_name = boto3_service_name
        self._temp_role_config.required_services  = required_services
        return self

    def _temp_role__iam_reset_credentials(self):
        return self._iam_assume_role().credentials_reset()

    # methods that override the normal Boto3 helper classes in OSBot_AWS
    @cache_on_self
    def client(self):
        self._create_role_and_credentials()
        service_name    = self._temp_role_config.boto3_service_name
        iam_assume_role = self._iam_assume_role()
        return iam_assume_role.boto3_client(service_name=service_name)

    @cache_on_self
    def resource(self):
        self._create_role_and_credentials()
        service_name = self._temp_role_config.boto3_service_name
        iam_assume_role = self._iam_assume_role()
        return iam_assume_role.boto3_resource(service_name=service_name)



