from osbot_utils.utils.Zip                                              import zip_bytes__files, zip_bytes__files_paths
from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency__Base        import Lambda__Dependency__Base
from osbot_aws.aws.lambda_.schemas.Safe_Str__File__Path__Python_Package import Safe_Str__File__Path__Python_Package
from osbot_aws.aws.s3.S3                                                import S3, S3_FILES_CONTENT_TYPES

FOLDER_NAME__LAMBDA_DEPENDENCIES = Safe_Str__File__Path__Python_Package('lambdas-dependencies')

class Lambda__Dependency__S3(Lambda__Dependency__Base):
    s3           : S3

    def bucket__name(self):
        return self.aws_config.lambda_s3_bucket()

    def bucket__exists(self):
        return self.s3.bucket_exists(self.bucket__name())

    def bytes(self):
        return self.s3.file_bytes(self.bucket__name(), self.path())

    def delete(self):
        return self.s3.file_delete(self.bucket__name(), self.path())

    def exists(self):
        return self.s3.file_exists(self.bucket__name(), self.path())

    def files(self):
        return zip_bytes__files(self.bytes())

    def files__paths(self):
        return zip_bytes__files_paths(self.bytes())

    def folder_name__lambda_dependencies(self):
        return FOLDER_NAME__LAMBDA_DEPENDENCIES

    def metadata(self):
        return self.s3.file_metadata(self.bucket__name(), self.path())

    def path(self) -> Safe_Str__File__Path__Python_Package:
        return self.folder_name__lambda_dependencies() + f"/{self.package_name}.zip"

    def setup(self):
        bucket_name = self.bucket__name()
        if self.bucket__exists() is False:
            region_name = self.aws_config.region_name()
            self.s3.bucket_create(bucket= bucket_name, region=region_name)
        return self

    def upload(self, file_bytes):
        kwargs       = dict(file_bytes   = file_bytes,
                            bucket       = self.bucket__name(),
                            key          = self.path(),
                            metadata     = {'data_type': 'zip-folder-for-lambda-function'},
                            content_type = S3_FILES_CONTENT_TYPES.get('.zip'))
        self.s3.file_create_from_bytes(**kwargs)
        return kwargs

