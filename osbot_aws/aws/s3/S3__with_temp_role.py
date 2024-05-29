from functools import cache

from dotenv import load_dotenv

from osbot_aws.apis.S3 import S3
from osbot_aws.aws.apigateway.API_Gateway_V2 import API_Gateway_V2
from osbot_aws.aws.iam.IAM_Assume_Role import IAM_Assume_Role


class S3__with_temp_role(S3):
    temp_service_name   : str = "s3"
    temp_role__services : str = ["s3"]
    temp_role__action   : str = "*"
    temp_role__resource : str = "*"
    temp_role__name     : str = 'osbot__temp_role_for__test_S3'
    temp_role__recreate : bool = False

    def iam_assume_role(self):
        load_dotenv()
        action        = self.temp_role__action
        resource      = self.temp_role__resource
        role_name     = self.temp_role__name

        policies_to_add = []
        for temp_role__service in self.temp_role__services:
            policies_to_add.append(dict(service=temp_role__service, action=action, resource=resource))

        iam_assume_role = IAM_Assume_Role(role_name=role_name, policies_to_add=policies_to_add)
        return iam_assume_role

    def create_role(self, create_credentials=True):
        role_recreate   = self.temp_role__recreate
        iam_assume_role = self.iam_assume_role()
        iam_assume_role.create_role(recreate=role_recreate, create_credentials=create_credentials)
        return iam_assume_role

    #@print_boto3_calls()
    @cache
    def client(self):
        iam_assume_role = self.create_role()
        service        = self.temp_service_name
        return iam_assume_role.boto3_client(service_name=service)

    def temp_role__iam_reset_credentials(self):
        iam_assume_role = IAM_Assume_Role(role_name=self.temp_role__name)
        return iam_assume_role.credentials_reset()