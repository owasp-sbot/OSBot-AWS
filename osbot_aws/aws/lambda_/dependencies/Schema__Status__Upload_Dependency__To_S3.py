from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__Status__Upload_Dependency__To_S3(Type_Safe):
    duration__install_locally : float
    duration__upload_to_s3    : float
    result__already_existed   : bool
    result__install_locally   : bool
    result__upload_to_s3      : bool
