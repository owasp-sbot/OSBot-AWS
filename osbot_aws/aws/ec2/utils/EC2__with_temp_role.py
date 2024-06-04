from osbot_aws.aws.ec2.EC2 import EC2
from osbot_aws.aws.iam.utils.Temp_Role__For_Service import Temp_Role__For_Service


class EC2__with_temp_role(Temp_Role__For_Service, EC2):

    def __init__(self):
        super().__init__()
        self._temp_role_config.boto3_service_name = 'ec2'
        self._temp_role_config.required_services  = ['ec2']
