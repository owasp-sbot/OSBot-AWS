from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path
from osbot_utils.utils.Files                                                      import current_temp_folder
from osbot_aws.AWS_Config                                                         import AWS_Config
from osbot_aws.aws.lambda_.schemas.Safe_Str__File__Name__Python_Package           import Safe_Str__File__Name__Python_Package
from osbot_utils.type_safe.Type_Safe                                              import Type_Safe


DEFAULT__TEMP_FOLDER  = Safe_Str__File__Path(current_temp_folder())

class Lambda__Dependency__Base(Type_Safe):
    aws_config                  : AWS_Config
    temp_folder                 : Safe_Str__File__Path                  = DEFAULT__TEMP_FOLDER
    package_name                : Safe_Str__File__Name__Python_Package = None

    def __init__(self, package_name):
        super().__init__(package_name=package_name)                                 # make sure package name is defined


