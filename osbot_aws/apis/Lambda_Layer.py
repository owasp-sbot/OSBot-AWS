import os
import shutil

from osbot_aws.Globals                      import Globals
from osbot_aws.apis.S3                      import S3
from osbot_aws.apis.Session                 import Session
from osbot_utils.decorators.Lists import index_by
from osbot_utils.utils.Files                import Files
from osbot_utils.decorators.Method_Wrappers import cache, remove, required_fields
from osbot_utils.utils.Misc                 import get_missing_fields


class Lambda_Layer:
    def __init__(self, layer_name='', runtimes=None, folders_mapping=None, license_info=None, s3_bucket=None, description=None, version_arn=None, version_number=None):
        self.layer_name      = layer_name.replace('.', '-')
        self.folders_mapping = folders_mapping  or {}
        self.runtimes        = runtimes         or ['python3.8', 'python3.7', 'python3.6']
        self.license_info    = license_info     or 'https://github.com/filetrust/gw-proxy-serverless/blob/master/LICENSE'
        self.description     = description      or ''
        self.s3_bucket       = s3_bucket        or Globals.lambda_layers_s3_bucket
        self.s3_key          = f'{self.layer_name}.zip'
        self.version_arn     = version_arn
        self.version_number  = version_number

    # cached dependencies

    @cache
    def client(self):
        return Session().client('lambda')

    @cache
    def s3(self):
        return S3()

    # main methods
    def create_from_folder(self, folder):
        pass

    @remove('ResponseMetadata')
    @required_fields(['layer_name'])
    def create_from_zip_bytes(self, zip_bytes):
        params = { 'LayerName'         : self.layer_name           ,
                   'Description'       : self.description          ,
                   'Content'           : {  'ZipFile' : zip_bytes },
                   'CompatibleRuntimes': self.runtimes             }
        return self.client().publish_layer_version(**params)

    # def create(self):
    #     missing_fields = get_missing_fields(self,['name', 'runtimes', 'license_info', 's3_bucket', 's3_key'])
    #     if len(missing_fields) > 0:
    #         raise  Exception('missing fields in create_lambda_layer: {0}'.format(missing_fields))
    #     # Folder mappings should only be required for local creations. Creations from apig need to
    #     # use this - we expect the layers zip already in the bucket during rest execution
    #     if self.folders_mapping is not None:
    #         zipped_layer_file = self.get_zipped_layer_filename()
    #         if not self.s3().bucket_exists(self.s3_bucket):
    #             self.s3().bucket_create(self.s3_bucket, Globals.aws_session_region_name)
    #         self.s3().file_upload_to_key(zipped_layer_file, self.s3_bucket, self.s3_key)
    #     params = {'LayerName': self.layer_name,
    #               'Description': self.description,
    #               'Content': {
    #                   'S3Bucket': self.s3_bucket,
    #                   'S3Key': self.s3_key
    #               },
    #               'CompatibleRuntimes': self.runtimes,
    #               'LicenseInfo': self.license_info
    #               }
    #     aws_response = self.client().publish_layer_version(**params)
    #     self.version_arn = aws_response.get("LayerVersionArn")
    #     self.version_number = aws_response.get("Version")
    #     if self.folders_mapping is not None:
    #         self.delete_zipped_layer_file()
    #     return self.version_arn

    def get_layer(self):
        return self.client().get_layer_version_by_arn(Arn=self.version_arn)

    def get_layer_version_arn(self):
        return self.version_arn

    def delete(self, with_s3_bucket=False):
        if self.exists() is False:
            return False
        if not self.version_arn or not self.version_number:
            return False
        self.client().delete_layer_version(LayerName=self.layer_name, VersionNumber=self.version_number)
        if self.s3().file_exists(self.s3_bucket, self.s3_key):
            self.s3().file_delete(self.s3_bucket, self.s3_key)
        if with_s3_bucket and self.s3().bucket_exists(self.s3_bucket):
            self.s3().bucket_delete(self.s3_bucket)
        return self.exists() is False

    def exists(self):
        try:
            self.get_layer()
            return True
        except:
            return False

    @index_by
    def layers(self):
        return self.client().list_layers().get('Layers')

    # def get_zipped_layer_filename(self):
    #     import gw_proxy
    #     layer_path = os.path.dirname(gw_proxy.__file__)
    #     for source, destination in self.folders_mapping.items():
    #         shutil.copytree(source, f"{layer_path}/layers/{self.nalayer_nameme}/{destination}")
    #     file = Files.zip_folder(f"{layer_path}/layers/{self.layer_name}")
    #     return file
    #
    # def delete_zipped_layer_file(self):
    #     import gw_proxy
    #     path = os.path.dirname(gw_proxy.__file__)
    #     Files.delete(f"{path}/layers/{self.layer_name}.zip")