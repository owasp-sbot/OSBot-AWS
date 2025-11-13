from osbot_aws.aws.comprehend.Comprehend            import Comprehend
from osbot_aws.aws.iam.IAM_Assume_Role              import IAM_Assume_Role
from osbot_utils.decorators.methods.cache_on_self   import cache_on_self
from osbot_utils.utils.Env                          import load_dotenv


class Comprehend__with_temp_role(Comprehend):


    def iam_assume_role(self):
        load_dotenv()
        services        = ["comprehend"]
        action          = "*"
        resource        = "*"
        role_name       = 'osbot__temp_role_for__test_Comprehend'
        policies_to_add = []
        for service in services:
            policies_to_add.append(dict(service=service, action=action, resource=resource))
        iam_assume_role = IAM_Assume_Role(role_name=role_name, policies_to_add=policies_to_add)
        iam_assume_role.create_role(recreate=False)
        #iam_assume_role.credentials_reset()
        return iam_assume_role


    @cache_on_self
    def client(self):
        service = "comprehend"
        return self.iam_assume_role().boto3_client(service_name=service)