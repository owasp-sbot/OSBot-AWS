from typing                                                                         import List
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_aws.aws.lambda_.schemas.Safe_Str__File__Path__Python_Package             import Safe_Str__File__Path__Python_Package
from osbot_aws.aws.lambda_.schemas.Safe_Str__File__Name__Python_Package             import Safe_Str__File__Name__Python_Package
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now             import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path   import Safe_Str__File__Path

class Schema__Lambda__Dependency__Local_Install__Data(Type_Safe):
    package_name        : Safe_Str__File__Name__Python_Package  = None
    target_path         : Safe_Str__File__Path__Python_Package  = None
    install_data        : dict                                  = None
    installed_files     : List[Safe_Str__File__Path]
    time_stamp          : Timestamp_Now
    duration            : float                                 = None
