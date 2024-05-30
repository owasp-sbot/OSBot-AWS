from osbot_aws.aws.iam.IAM_Role import IAM_Role
from osbot_aws.aws.iam.roles.IAM_Policy__Full_Access import IAM__Policy__Service__Full_Access
from osbot_aws.aws.iam.roles.IAM__Policy__Assume__Service import iam_statement__ec2__assume_service
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.utils.Dev import pprint


class IAM__Role_For(Kwargs_To_Self):
    assume_policy : dict
    iam_role      : IAM_Role = None
    skip_if_exists: bool     = True

    def create(self):
        kwargs = dict(assume_policy_document = {'Statement': [self.assume_policy] }  ,
                      skip_if_exists         = self.skip_if_exists )
        return self.iam_role.create(**kwargs)

    def exists(self):
        return self.iam_role.exists()

    def role_policies(self):
        return list(self.iam_role.iam.role_policies_attached())

class IAM__Role_for__EC2_Instances(IAM__Role_For):

    def __init__(self, role_name):
        self.assume_policy = iam_statement__ec2__assume_service()
        self.iam_role = IAM_Role(role_name)
        super().__init__()

    def attach_policy__full_access__s3(self):
        iam_policy = IAM__Policy__Service__Full_Access(service_name='s3')
        iam_policy.create()                                                 # create if doesn't exist
        iam_policy_arn = iam_policy.arn()
        return self.iam_role.iam.role_policy_attach(policy_arn=iam_policy_arn)

    def setup(self):
        if self.exists() is False:
            create_result = self.create()
            assert create_result.get('status') == 'ok'
            self.attach_policy__full_access__s3()
            self.iam_role.create_instance_profile()         # this is needed so that EC2 can use this role
            self.iam_role.add_to_instance_profile()
        return self

