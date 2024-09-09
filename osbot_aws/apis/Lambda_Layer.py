from osbot_utils.decorators.lists.index_by              import index_by
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from osbot_utils.decorators.methods.remove_return_value import remove_return_value
from osbot_utils.decorators.methods.required_fields     import required_fields
from osbot_aws.AWS_Config                               import AWS_Config
from osbot_aws.aws.s3.S3                                import S3
from osbot_aws.apis.Session                             import Session
from osbot_utils.testing.Temp_Folder                    import Temp_Folder
from osbot_utils.testing.Temp_Zip                       import Temp_Zip
from osbot_utils.utils.Files                            import file_bytes, temp_folder, temp_file, file_name, path_combine, folder_copy
from osbot_utils.utils.Http                             import GET_bytes_to_file
from osbot_utils.utils.Process                          import run_process
from osbot_utils.utils.Zip                              import folder_zip


class Lambda_Layer:
    def __init__(self, layer_name='', runtimes=None, license_info=None, s3_bucket=None, s3_folder=None, description=None, region=None, account_id=None):
        self.aws_config      = AWS_Config()
        self.layer_name      = layer_name.replace('.', '-')
        self.runtimes        = runtimes         or ['python3.11', 'python3.10', 'python3.9']# 'python3.8', 'python3.7', 'python3.6']
        self.license_info    = license_info     or 'https://github.com/owasp-sbot/OSBot-AWS/blob/master/LICENSE'
        self.description     = description      or ''
        self.s3_bucket       = s3_bucket        or self.aws_config.lambda_s3_bucket()
        self.s3_folder       = s3_folder        or self.aws_config.lambda_s3_folder_layers()
        self.region          = region           or self.aws_config.aws_session_region_name()
        self.account_id      = account_id       or self.aws_config.aws_session_account_id()
        self.s3_key          = f'{self.s3_folder}/{self.layer_name}.zip'
        #self.version_number  = version_number       # todo fix the use of this value


    # cached dependencies

    def arn(self, version):
        return f'arn:aws:lambda:{self.region}:{self.account_id}:layer:{self.layer_name}:{version}'

    def arn_latest(self):
        version = self.latest_version()
        if version:
            return self.arn(version)

    @cache_on_self
    def client(self):
        return Session().client('lambda')

    def content(self, version=None):
        return self.info(version).get('Content')

    @remove_return_value('ResponseMetadata')
    def version_by_arn(self):
        kwargs = {'Arn': self.arn_latest()}
        return self.client().get_layer_version_by_arn(**kwargs)

    @cache_on_self
    def s3(self):
        return S3()

    def create_from_folder(self, folder):
        zip_file  = folder_zip(folder)
        zip_bytes = file_bytes(zip_file)
        return self.create_from_zip_bytes(zip_bytes)

    # def create_from_folder_via_s3(self, folder):
    #     zip_file = folder_zip(folder)
    #     return self.create_from_zip_file_via_s3(zip_file)

    def create_from_folder_via_s3(self, source_folder, ignore_pattern=None):
        if ignore_pattern is None:
            ignore_pattern = ['*.pyc', '.DS_Store', '__pycache__', '.env']

        with Temp_Folder(temp_prefix='lambda_layer') as _:
            destination = path_combine(_.path(), 'python')
            folder_copy(source=source_folder, destination=destination, ignore_pattern=ignore_pattern)
            with Temp_Zip(_.path()) as zip_file:
                result = self.create_from_zip_file_via_s3(zip_file.path())
                return  result.get('LayerVersionArn')

    def create_from_pip(self, package_name, pip_executable='pip3'):
        path_install = temp_folder()
        install_result = run_process(pip_executable, ['install','-t',path_install,package_name])
        if install_result.get('error') is None and install_result.get('stderr').startswith('ERROR') is False:
            return self.create_from_folder(path_install)
        else:
            return {'status': 'error', 'error':install_result.get('stderr'), 'stdout': install_result.get('stdout')}

    def create_from_zip_file_via_s3(self, zip_file):
        self.upload_layer_zip_file_to_s3(zip_file)
        return self.create_from_s3()

    @remove_return_value('ResponseMetadata')
    @required_fields(['layer_name'])
    def create_from_zip_bytes(self, zip_bytes):
        params = { 'LayerName'         : self.layer_name           ,
                   'Description'       : self.description          ,
                   'Content'           : {  'ZipFile' : zip_bytes },
                   'LicenseInfo'       : self.license_info         ,
                   'CompatibleRuntimes': self.runtimes             }
        return self.client().publish_layer_version(**params)

    @remove_return_value('ResponseMetadata')
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


    @remove_return_value('ResponseMetadata')
    def info(self, version=None):
        return self.version(version)

    #def info_by_arn(self, version=None):

    def info_by_arn(self):
       return self.version_by_arn()

    def latest_version(self):
        return self.latest().get('Version')

    def latest(self):
        results = self.versions(max_items=1)
        if len(results) > 0:
            return results[0]
        return {}

    @index_by
    def layers(self):
        return self.client().list_layers().get('Layers')

    def policy(self, version=None):
        kwargs = {'LayerName'    : self.layer_name,
                  'VersionNumber': version or self.latest_version()}
        return self.client().get_layer_version_policy(**kwargs)  # return self.latest()


    def s3_folder_files(self):
        return self.s3().find_files(self.s3_bucket, self.s3_folder)

    def version(self, version=None):
        kwargs = {'LayerName': self.layer_name,
                  'VersionNumber': version or self.latest_version()}
        return self.client().get_layer_version(**kwargs)

    def versions(self, max_items=None):
        kwargs = {'LayerName': self.layer_name}
        if max_items:
            kwargs['MaxItems'] = max_items
        return self.client().list_layer_versions(**kwargs).get('LayerVersions')