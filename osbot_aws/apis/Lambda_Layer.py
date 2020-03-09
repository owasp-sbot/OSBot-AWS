import os
import shutil

from osbot_aws.apis.Session import Session
from osbot_aws.tmp_utils.Temp_Misc import Temp_Misc
from osbot_utils.decorators.Method_Wrappers import cache, catch
from osbot_utils.utils.Files import Files
from osbot_aws.apis.S3 import S3
from gw_proxy.Globals import Globals
import gw_proxy



class Lambda_Layer:
    def __init__(self, name=None, folders_mapping={}, s3_bucket=None, description=''):
        self.name           = name.replace('.', '-')
        self.folders_mapping = folders_mapping
        self.runtimes       = ['python3.8', 'python3.7', 'python3.6']
        self.license_info   =  'https://github.com/filetrust/gw-proxy-serverless/blob/master/LICENSE'
        self.description    = description
        self.s3_bucket      = s3_bucket if s3_bucket else Globals.lambda_layers_s3_bucket
        self.s3_key         = f'{name}.zip'
        self.version_arn    = None
        self.version_number = None

    # cached dependencies

    @cache
    def client(self):
        return Session().client('lambda')

    @cache
    def s3(self):
        return S3()

    def _call_method_with_paginator(self, method, field_id, **kwargs):
        api       = self.client()
        paginator = api.get_paginator(method)
        for page in paginator.paginate(**kwargs):
            for id in page.get(field_id):
                yield id


    # main methods

    def create(self):
        missing_fields = Temp_Misc.get_missing_fields(self,['name', 'folders_mapping', 'runtimes', 'license_info', 's3_bucket', 's3_key'])
        if len(missing_fields) > 0:
            raise  Exception('missing fields in create_lambda_layer: {0}'.format(missing_fields))
        zipped_layer_file = self.get_zipped_layer_filename()
        if not self.s3().bucket_exists(self.s3_bucket):
            self.s3().bucket_create(self.s3_bucket, Globals.aws_session_region_name)
        self.s3().file_upload_to_key(zipped_layer_file, self.s3_bucket, self.s3_key)
        params = {'LayerName': self.name,
                  'Description': self.description,
                  'Content': {
                      'S3Bucket': self.s3_bucket,
                      'S3Key': self.s3_key
                  },
                  'CompatibleRuntimes': self.runtimes,
                  'LicenseInfo': self.license_info
                  }
        aws_response = self.client().publish_layer_version(**params)
        self.version_arn = aws_response.get("LayerVersionArn")
        self.version_number = aws_response.get("Version")
        self.delete_zipped_layer_file()
        return self.version_arn

    def get_layer(self):
        return self.client().get_layer_version_by_arn(Arn=self.version_arn)

    def get_layer_version_arn(self):
        return self.version_arn

    def delete(self, with_s3_bucket=False):
        if self.exists() is False:
            return False
        self.client().delete_layer_version(LayerName=self.name, VersionNumber=self.version_number)
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

    def layers(self):
        return self.client().list_layers().get('Layers')

    def get_zipped_layer_filename(self):
        layer_path = os.path.dirname(gw_proxy.__file__)
        for source, destination in self.folders_mapping.items():
            shutil.copytree(source, f"{layer_path}/layers/{self.name}/{destination}")
        file = Files.zip_folder(f"{layer_path}/layers/{self.name}")
        return file

    def delete_zipped_layer_file(self):
        path = os.path.dirname(gw_proxy.__file__)
        Files.delete(f"{path}/layers/{self.name}.zip")