import os
import shutil

from osbot_aws.Globals                      import Globals
from osbot_aws.apis.S3                      import S3
from osbot_aws.apis.Session                 import Session
from osbot_utils.decorators.Lists import index_by
from osbot_utils.utils.Files import Files, folder_zip, file_bytes, temp_folder, temp_file
from osbot_utils.decorators.Method_Wrappers import cache, remove, required_fields
from osbot_utils.utils.Http import GET_bytes_to_file
from osbot_utils.utils.Misc                 import get_missing_fields
from osbot_utils.utils.Process import run_process


class Lambda_Layer:
    def __init__(self, layer_name='', runtimes=None, license_info=None, s3_bucket=None, description=None, version_arn=None, version_number=None):
        self.layer_name      = layer_name.replace('.', '-')
        #self.folders_mapping = folders_mapping  or {}
        self.runtimes        = runtimes         or ['python3.8', 'python3.7', 'python3.6']
        self.license_info    = license_info     or 'https://github.com/filetrust/gw-proxy-serverless/blob/master/LICENSE'
        self.description     = description      or ''
        self.s3_bucket       = s3_bucket        or Globals.lambda_s3_bucket
        self.s3_folder       = 'layers'
        self.s3_key          = f'{self.s3_folder}/{self.layer_name}.zip'
        self.version_number  = version_number

    # cached dependencies

    @cache
    def client(self):
        return Session().client('lambda')

    @cache
    def s3(self):
        return S3()

    def create_from_folder(self, folder):
        zip_file  = folder_zip(folder)
        zip_bytes = file_bytes(zip_file)
        return self.create_from_zip_bytes(zip_bytes)

    def create_from_folder_via_s3(self, folder):
        zip_file = folder_zip(folder)
        self.upload_layer_zip_file_to_s3(zip_file)
        return self.create_from_s3()

    def create_from_pip(self, package_name, pip_executable='pip3'):
        path_install = temp_folder()
        install_result = run_process(pip_executable, ['install','-t',path_install,package_name])
        if install_result.get('stderr') == '':
            return self.create_from_folder(path_install)
        else:
            return {'status': 'error', 'error':install_result.get('stderr'), 'stdout': install_result.get('stdout')}

    @remove('ResponseMetadata')
    @required_fields(['layer_name'])
    def create_from_zip_bytes(self, zip_bytes):
        params = { 'LayerName'         : self.layer_name           ,
                   'Description'       : self.description          ,
                   'Content'           : {  'ZipFile' : zip_bytes },
                   'LicenseInfo'       : self.license_info         ,
                   'CompatibleRuntimes': self.runtimes             }
        return self.client().publish_layer_version(**params)

    @remove('ResponseMetadata')
    @required_fields(['layer_name'])
    def create_from_s3(self):
        params = {'LayerName'           : self.layer_name               ,
                    'Description'       : self.description              ,
                    'Content'           : { 'S3Bucket': self.s3_bucket  ,
                                            'S3Key'   : self.s3_key    },
                    'CompatibleRuntimes': self.runtimes                 ,
                    'LicenseInfo'       : self.license_info
                  }
        return self.client().publish_layer_version(**params)

    def upload_layer_zip_file_to_s3(self, zip_file):
        return self.s3().file_upload_to_key(zip_file, self.s3_bucket, self.s3_key)

    def code_zip(self):
        version_arn = self.latest().get('LayerVersionArn')
        if version_arn:
            url_code = self.client().get_layer_version_by_arn(Arn=version_arn).get('Content',{}).get('Location')
            if url_code:
                path_target = temp_file(extension='.zip')
                return GET_bytes_to_file(url_code, path_target)


    def delete(self):
        for version_info in self.versions():
            self.delete_version(version_info.get('Version'))

        return self.exists() is False



    def delete_version(self, version):
        return self.client().delete_layer_version(LayerName=self.layer_name, VersionNumber=version)

    def exists(self):
        return self.latest() != {}

    def latest(self):
        return self.layers(index_by='LayerName').get(self.layer_name,{}).get('LatestMatchingVersion', {})


    @index_by
    def layers(self):
        return self.client().list_layers().get('Layers')

    def s3_folder_files(self):
        return self.s3().find_files(self.s3_bucket, self.s3_folder)

    def versions(self):
        return self.client().list_layer_versions(LayerName=self.layer_name).get('LayerVersions')