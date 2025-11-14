from osbot_utils.type_safe.Type_Safe                import Type_Safe
from osbot_aws.aws.iam.IAM_Assume_Role              import IAM_Assume_Role
from osbot_utils.decorators.methods.cache_on_self   import cache_on_self
from osbot_utils.utils.Env                          import load_dotenv
from osbot_aws.aws.comprehend.Comprehend__Batch     import Comprehend__Batch
from osbot_aws.aws.comprehend.Comprehend            import Comprehend



class Comprehend__IAM__Temp_Role(Type_Safe):

    def iam_assume_role(self, role_name: str = None):   # Create or reuse temporary IAM role with Comprehend permissions.
        load_dotenv()

        # Default role name based on the class name
        if role_name is None:
            class_name = self.__class__.__name__
            role_name = f'osbot__temp_role_for__{class_name}'

        services        = ["comprehend"]
        action          = "*"
        resource        = "*"
        policies_to_add = []

        for service in services:
            policies_to_add.append(dict(service  = service  ,
                                       action   = action   ,
                                       resource = resource))

        iam_assume_role = IAM_Assume_Role(role_name       = role_name       ,
                                          policies_to_add = policies_to_add)
        iam_assume_role.create_role(recreate=False)

        return iam_assume_role

    @cache_on_self
    def client(self):   # Create Comprehend client using temporary IAM role credentials.
        service = "comprehend"
        return self.iam_assume_role().boto3_client(service_name=service)


# todo: see if there is a way to create these class (and use-case) without needing to create these extra classes

class Comprehend__with_temp_role(Comprehend__IAM__Temp_Role, Comprehend):
    pass

class Comprehend__Batch__with_temp_role(Comprehend__Batch):
    def __init__(self, **kwargs):
        self.client = Comprehend__IAM__Temp_Role().client()
        super().__init__(**kwargs)