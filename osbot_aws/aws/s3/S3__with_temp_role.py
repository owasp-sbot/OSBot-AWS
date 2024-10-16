from functools                          import cache
from osbot_aws.aws.s3.S3                import S3
from osbot_aws.aws.iam.IAM_Assume_Role  import IAM_Assume_Role
from osbot_utils.utils.Env              import load_dotenv


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

    
    @cache
    def client(self):
        iam_assume_role = self.create_role()
        service        = self.temp_service_name
        return iam_assume_role.boto3_client(service_name=service)

    def sts(self):
         return self.iam_assume_role().aws__client__sts()            # this is an STS object to the current identity (not the one used to create it)

    def temp_role__iam_reset_credentials(self):
        iam_assume_role = IAM_Assume_Role(role_name=self.temp_role__name)
        return iam_assume_role.credentials_reset()