from osbot_utils.base_classes.Type_Safe import Type_Safe
from osbot_utils.utils.Misc import random_text, lower

TEMP_ROLE__NAME_FORMAT = 'ROLE__temp_osbot__{role_access_type}__{boto3_service_name}'

class Temp_Role__For_Service__Config(Type_Safe):
    boto3_service_name : str
    required_services  : list
    action             : str = "*"
    resource           : str = "*"
    recreate           : bool = False
    random_role_name   : bool = False
    role_name          : str
    role_access_type   : str = 'Full_Access'

    def data(self):
        if not self.boto3_service_name:
            raise ValueError("boto3_service_name is required")
        if not self.required_services:
            raise ValueError("required_services is required")
        if not self.role_name:
            self.role_name = TEMP_ROLE__NAME_FORMAT.format(role_access_type=self.role_access_type, boto3_service_name=self.boto3_service_name)
            if self.random_role_name is True:
                self.role_name += lower(random_text('_'))
        return self