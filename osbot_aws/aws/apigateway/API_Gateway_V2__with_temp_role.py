from functools                                  import cache
from osbot_utils.utils.Env                      import load_dotenv
from osbot_aws.aws.apigateway.API_Gateway_V2    import API_Gateway_V2
from osbot_aws.aws.iam.IAM_Assume_Role          import IAM_Assume_Role


class API_Gateway_V2__with_temp_role(API_Gateway_V2):
    temp_service_name   : str = "apigatewayv2"
    temp_role__services : str = ["apigateway", "apigatewayv2", "apigatewaymanagementapi"]
    temp_role__action   : str = "*"
    temp_role__resource : str = "*"
    temp_role__name     : str = 'osbot__temp_role_for__test_API_Gateway_V2'
    temp_role__recreate : bool = False

    
    @cache
    def client(self):
        load_dotenv()
        service       = self.temp_service_name
        action        = self.temp_role__action
        resource      = self.temp_role__resource
        role_name     = self.temp_role__name
        role_recreate = self.temp_role__recreate
        policies_to_add = []
        for temp_role__service in self.temp_role__services:
            policies_to_add.append(dict(service=temp_role__service, action=action, resource=resource))

        iam_assume_role = IAM_Assume_Role(role_name=role_name, policies_to_add=policies_to_add)
        iam_assume_role.create_role(recreate=role_recreate)
        #iam_assume_role.credentials_reset()
        return iam_assume_role.boto3_client(service_name=service)

    def temp_role__iam_reset_credentials(self):
        iam_assume_role = IAM_Assume_Role(role_name=self.temp_role__name)
        return iam_assume_role.credentials_reset()