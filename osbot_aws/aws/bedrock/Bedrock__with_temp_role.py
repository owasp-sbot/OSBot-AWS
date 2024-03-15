from dotenv import load_dotenv

from osbot_aws.aws.bedrock.Bedrock import Bedrock
from osbot_aws.aws.iam.IAM_Assume_Role import IAM_Assume_Role
from osbot_utils.decorators.methods.cache_on_self import cache_on_self


class Bedrock__with_temp_role(Bedrock):

    def iam_assume_role(self, service):
        load_dotenv()
        #policies_to_add = [dict(service=service, action=action, resource=resource)]
        services        = ["bedrock", "bedrock-runtime"]
        action          = "*"
        resource        = "*"
        role_name       = 'osbot__temp_role_for__test_Bedrock'
        policies_to_add = []
        for service in services:
            policies_to_add.append(dict(service=service, action=action, resource=resource))
        iam_assume_role = IAM_Assume_Role(role_name=role_name, policies_to_add=policies_to_add)
        iam_assume_role.create_role(recreate=False)
        #iam_assume_role.credentials_reset()
        return iam_assume_role

    @cache_on_self
    def client(self):
        service = "bedrock"
        return self.iam_assume_role(service).boto3_client(service_name=service, region_name=self.region_name)

    @cache_on_self
    def runtime(self):
        service = "bedrock-runtime"
        return self.iam_assume_role(service).boto3_client(service_name=service, region_name=self.region_name)
