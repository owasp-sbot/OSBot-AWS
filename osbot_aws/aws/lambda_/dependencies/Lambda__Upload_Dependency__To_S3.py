from typing                                                                      import Dict
from osbot_utils.helpers.duration.decorators.capture_duration                    import capture_duration
from osbot_utils.helpers.safe_str.Safe_Str__File__Path                           import Safe_Str__File__Path
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.utils.Files                                                     import path_combine, folder_exists
from osbot_aws.aws.lambda_.dependencies.Lambda__Dependencies import Lambda__Dependencies, DEFAULT__PATH__DEPENDENCIES
from osbot_aws.aws.lambda_.dependencies.Schema__Status__Upload_Dependency__To_S3 import Schema__Status__Upload_Dependency__To_S3



# todo: add support for using use python wheels which could also work really well
class Lambda__Upload_Dependency__To_S3(Type_Safe):
    dependencies : Lambda__Dependencies
    path_packages: Safe_Str__File__Path = Safe_Str__File__Path(path_combine('.', DEFAULT__PATH__DEPENDENCIES))


    def local_path(self, package):
        return path_combine(self.path_packages, package)

    def exists_locally(self, package):
        return folder_exists(self.local_path(package))

    def exists_in_s3(self, package):
        return self.dependencies.dependency_exists_in_s3(package)

    def install_locally(self, package):
        if self.exists_locally(package) is False:
            self.dependencies.pip_install_dependency(package)
        return self.exists_locally(package)

    def upload_to_s3(self, package):
        if type(package) is list:
            for item in package:
                self.upload_to_s3(item)
        else:
            if self.install_locally(package):
                return self.dependencies.upload_dependency(package)

    def upload_lambda_dependencies_to_s3(self, packages) -> Dict[str,Schema__Status__Upload_Dependency__To_S3]:

        status_packages = {}
        for package in packages:
            status_package = Schema__Status__Upload_Dependency__To_S3()
            if self.exists_in_s3(package):
                status_package.result__already_existed = True
            else:
                with capture_duration() as duration__install_locally:
                    status_package.result__install_locally = self.install_locally(package)
                status_package.duration__install_locally = duration__install_locally.seconds

                with capture_duration() as duration__upload_to_s3:
                    status_package.result__upload_to_s3 = self.upload_to_s3(package)
                status_package.result__upload_to_s3 = duration__upload_to_s3.seconds

            status_packages[package] = status_package
        return status_packages