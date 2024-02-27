from functools import cache

from dotenv import load_dotenv

from osbot_aws.aws.dynamo_db.Dynamo_DB import Dynamo_DB
from osbot_aws.aws.iam.IAM_Assume_Role import IAM_Assume_Role


class Dynamo_DB__with_temp_role(Dynamo_DB):

    #@print_boto3_calls()
    @cache
    def client(self):
        load_dotenv()
        service         = "dynamodb"
        action          = "*"
        resource        = "*"
        role_name       = 'osbot__temp_role_for__test_Dynamo_DB'
        policies_to_add = [dict(service=service, action=action, resource=resource)]
        iam_assume_role = IAM_Assume_Role(role_name=role_name, policies_to_add=policies_to_add)
        iam_assume_role.create_role(recreate=False)
        iam_assume_role.credentials_reset()
        return iam_assume_role.boto3_client(service_name=service)