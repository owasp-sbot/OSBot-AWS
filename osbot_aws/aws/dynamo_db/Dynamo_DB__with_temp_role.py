from functools                          import cache
from osbot_utils.utils.Env              import load_dotenv
from osbot_aws.aws.dynamo_db.Dynamo_DB  import Dynamo_DB
from osbot_aws.aws.iam.IAM_Assume_Role  import IAM_Assume_Role


class Dynamo_DB__with_temp_role(Dynamo_DB):
    temp_role__service  : str = "dynamodb"
    temp_role__action   : str = "*"
    temp_role__resource : str = "*"
    temp_role__name     : str = 'osbot__temp_role_for__test_Dynamo_DB'
    temp_role__recreate : bool = False

    
    @cache
    def client(self):
        load_dotenv()
        service       = self.temp_role__service
        action        = self.temp_role__action
        resource      = self.temp_role__resource
        role_name     = self.temp_role__name
        role_recreate = self.temp_role__recreate
        policies_to_add = [dict(service=service, action=action, resource=resource)]
        iam_assume_role = IAM_Assume_Role(role_name=role_name, policies_to_add=policies_to_add)
        iam_assume_role.create_role(recreate=role_recreate)
        #iam_assume_role.credentials_reset()
        return iam_assume_role.boto3_client(service_name=service)

    def temp_role__iam_reset_credentials(self):
        iam_assume_role = IAM_Assume_Role(role_name=self.temp_role__name)
        return iam_assume_role.credentials_reset()