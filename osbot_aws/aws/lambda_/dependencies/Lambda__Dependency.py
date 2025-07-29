from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency__Local       import Lambda__Dependency__Local
from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency__S3          import Lambda__Dependency__S3
from osbot_aws.aws.lambda_.schemas.Safe_Str__File__Name__Python_Package import Safe_Str__File__Name__Python_Package
from osbot_utils.type_safe.Type_Safe                                    import Type_Safe


class Lambda__Dependency(Type_Safe):
    package_name      : Safe_Str__File__Name__Python_Package  = None
    dependency__local : Lambda__Dependency__Local             = None
    dependency__s3    : Lambda__Dependency__S3                = None

    def __init__(self, package_name):
        super().__init__(package_name=package_name)
        self.dependency__local = Lambda__Dependency__Local(package_name=package_name)
        self.dependency__s3    = Lambda__Dependency__S3   (package_name=package_name)

    def install_and_upload(self, refresh=False):
        with self.dependency__local as _:
            _.setup()
            if refresh:
                _.delete()
            local_result = _.install()

        with self.dependency__s3 as _:
            _.setup()
            if refresh:
                _.delete()
            if _.exists() is False:
                file_bytes = self.dependency__local.files__zipped()
                _.upload(file_bytes=file_bytes)
            s3_exists = _.exists()

        return dict(local_result=local_result, s3_exists=s3_exists)
