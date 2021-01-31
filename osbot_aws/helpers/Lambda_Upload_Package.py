from osbot_aws.Dependencies import pip_install_dependency, upload_dependency

from osbot_utils.utils.Files import path_combine, folder_exists


class Lambda_Upload_Package:

    def __init__(self):
        self.path_packages = path_combine('.', '../../../_lambda_dependencies/')

    def local_path(self, package):
        return path_combine(self.path_packages, package)

    def exists_locally(self, package):
        return folder_exists(self.local_path(package))

    def install_locally(self, package):
        if self.exists_locally(package) is False:
            pip_install_dependency(package)
        return self.exists_locally(package)

    def upload_to_s3(self, package):
        if type(package) is list:
            for item in package:
                self.upload_to_s3(item)
        else:
            if self.install_locally(package):
                return upload_dependency(package)

    # def test_install_locally(self):
    #     assert self.lambda_setup.install_locally(self.package) is True
    #     assert self.lambda_setup.exists_locally (self.package) is True
    #
    # def test_upload_to_s3(self):
    #     pprint(self.lambda_setup.    upload_to_s3(self.package))
