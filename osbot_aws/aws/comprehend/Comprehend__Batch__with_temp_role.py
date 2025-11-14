from osbot_aws.aws.comprehend.Comprehend__Batch                 import Comprehend__Batch
from osbot_aws.aws.iam.IAM_Assume_Role                         import IAM_Assume_Role
from osbot_utils.decorators.methods.cache_on_self              import cache_on_self
from osbot_utils.utils.Env                                     import load_dotenv


# todo: refactor this with Comprehend__with_temp_role.py since the code is just about the same
class Comprehend__Batch__with_temp_role(Comprehend__Batch):
    """
    Comprehend Batch client with temporary IAM role for testing.
    
    This class creates a temporary IAM role with the necessary Comprehend permissions
    and uses it to make API calls. This is useful for:
    - Testing without permanent AWS credentials
    - Isolating test permissions from production
    - Simulating least-privilege scenarios
    - CI/CD environments where temporary credentials are preferred
    
    The temporary role is created with these permissions:
    - Service: comprehend
    - Action: * (all comprehend actions)
    - Resource: * (all resources)
    
    Note: The role is created once and reused across test runs unless recreate=True
    """

    def iam_assume_role(self):
        """
        Create or reuse temporary IAM role with Comprehend permissions.
        
        Returns:
            IAM_Assume_Role: Configured IAM role with Comprehend access
        """
        load_dotenv()
        services        = ["comprehend"]
        action          = "*"
        resource        = "*"
        role_name       = 'osbot__temp_role_for__test_Comprehend__Batch'
        policies_to_add = []
        for service in services:
            policies_to_add.append(dict(service=service, action=action, resource=resource))
        iam_assume_role = IAM_Assume_Role(role_name=role_name, policies_to_add=policies_to_add)
        iam_assume_role.create_role(recreate=False)
        return iam_assume_role

    @cache_on_self
    def client(self):
        """
        Create Comprehend client using temporary IAM role credentials.
        
        Returns:
            boto3.client: Comprehend client with temporary credentials
        """
        service = "comprehend"
        return self.iam_assume_role().boto3_client(service_name=service)
