import sys
from osbot_utils.utils.Zip                                       import zip_bytes__extract_to_folder
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id                                 import Safe_Id
from osbot_utils.utils.Files                                     import path_combine, folder_exists, files_list__virtual_paths
from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency__Base import Lambda__Dependency__Base
from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency__S3   import Lambda__Dependency__S3

FOLDER_NAME__LAMBDA_DEPENDENCIES__INSIDE_LAMBDA  = Safe_Id('osbot-aws__lambda-dependencies__inside-lambda')

class Lambda__Dependency__Inside_Lambda(Lambda__Dependency__Base):
    skip__when_not_inside_lambda: bool                   = True
    lambda_dependency_s3        : Lambda__Dependency__S3 = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lambda_dependency_s3 = Lambda__Dependency__S3(package_name=self.package_name)

    def dependencies_folder(self):
        return path_combine(self.temp_folder, FOLDER_NAME__LAMBDA_DEPENDENCIES__INSIDE_LAMBDA)

    def exists(self):
        return folder_exists(self.folder())

    def enabled(self):
        return self.exists() and self.system_path__contains_folder()

    def files(self):
        return files_list__virtual_paths(self.folder())

    def folder(self):
        return path_combine(self.dependencies_folder(), self.package_name)

        #s3_key     = 'lambdas-dependencies/{0}.zip'.format(target)
        #tmp_dir    = Files.path_combine('/tmp/lambdas-dependencies', target)

    def load(self):
        target_folder = self.folder()
        if self.exists() is False:
            with self.lambda_dependency_s3 as _:
                 if _.exists() is False:
                    raise RuntimeError(f"in Lambda__Dependency__Load the requested package {self.package_name} "
                                       f"was not found in: {_.bucket__name()} : {_.path()}")
                 zip_bytes__extract_to_folder(zip_bytes=_.bytes(), target_folder=target_folder)
        self.system_path__add_folder()
        return self.enabled()

    def system_path(self):
        return sys.path

    def system_path__add_folder(self):
        if self.system_path__contains_folder() is False:
            sys.path.append(self.folder())
            return True
        return False

    def system_path__contains_folder(self):
        return self.folder() in self.system_path()
