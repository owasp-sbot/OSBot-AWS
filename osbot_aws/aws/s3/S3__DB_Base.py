from osbot_aws.aws.session.Session__Kwargs__S3      import Session__Kwargs__S3
from osbot_utils.base_classes.Type_Safe             import Type_Safe
from osbot_utils.decorators.methods.cache_on_self   import cache_on_self

ENV_NAME__USE_MINIO_AS_S3            = 'USE_MINIO_AS_S3'
S3_DB_BASE__BUCKET_NAME__SUFFIX      = "osbot-aws"
S3_DB_BASE__BUCKET_NAME__PREFIX: str = 'unknown-service'
S3_DB_BASE__SERVER_NAME              = 'unknown-server'
S3_FOLDER__TEMP_FILE_UPLOADS         = 'temp_file_uploads'
DEFAULT__LOCAL_STACK__TARGET_SERVER = 'http://localhost:4566'

class S3__DB_Base(Type_Safe):
    use_minio                      : bool = False
    bucket_name__suffix            : str  = S3_DB_BASE__BUCKET_NAME__SUFFIX
    bucket_name__prefix            : str  = S3_DB_BASE__BUCKET_NAME__PREFIX
    bucket_name__insert_account_id : bool = True
    bucket_versioning              : bool = True
    save_as_gz                     : bool = False
    server_name                    : str  = S3_DB_BASE__SERVER_NAME
    session_kwargs__s3             : Session__Kwargs__S3

    def bucket_name(self):
        return self.s3_bucket()

    @cache_on_self
    def s3(self):
        from osbot_aws.aws.s3.S3   import S3
        from osbot_utils.utils.Env import get_env

        if self.use_minio or get_env(ENV_NAME__USE_MINIO_AS_S3) == 'True':
            from osbot_aws.aws.s3.S3__Minio import S3__Minio

            self.use_minio = True                                               # todo: remove this hardcoded minio dependency, since in most cases we are using LocalStack
            s3 = S3__Minio().s3()
        else:
            s3 = S3(session_kwargs__s3=self.session_kwargs__s3)
        return s3

    @cache_on_self
    def s3_bucket(self):
        from osbot_aws.AWS_Config             import aws_config
        from osbot_aws.utils.AWS_Sanitization import str_to_valid_s3_bucket_name

        separator  = '-'
        bucket_name = ''
        if self.bucket_name__prefix:
            bucket_name += f'{self.bucket_name__prefix}{separator}'
        if self.bucket_name__insert_account_id:
            account_id  = aws_config.account_id()
            bucket_name += f'{account_id}{separator}'
        bucket_name += self.bucket_name__suffix
        return str_to_valid_s3_bucket_name(bucket_name)                                           # make sure it is a valid s3 bucket name

    def s3_bucket__temp_data(self):                                                               # override to control the bucket used for temp data (note that it is the caller responsibility to make sure the bucket exists)
        return self.s3_bucket()

    def s3_file_bytes(self, s3_key, version_id=None):
        return self.s3().file_bytes(self.s3_bucket(), s3_key, version_id)

    def s3_file_contents(self, s3_key, version_id=None):
        return self.s3().file_contents(self.s3_bucket(), s3_key, version_id=version_id)

    def s3_file_contents_json(self, s3_key, version_id=None):
        from osbot_utils.utils.Json import json_parse

        return json_parse(self.s3_file_contents(s3_key, version_id=version_id))

    def s3_file_contents_obj(self, s3_key, version_id=None):                                                     # Convert S3 file contents to a Python object using str_to_obj
        from osbot_utils.utils.Objects import str_to_obj
        return str_to_obj(self.s3_file_contents(s3_key, version_id=version_id))

    def s3_file_data(self, s3_key, version_id=None):
        from osbot_utils.utils.Files import file_extension
        from osbot_utils.utils.Json  import gz_to_json

        if self.s3_file_exists(s3_key):
            if self.save_as_gz and file_extension(s3_key) == '.gz':
                data_gz = self.s3_file_bytes(s3_key,version_id=version_id)
                data    = gz_to_json(data_gz)
            else:
                data = self.s3_file_contents_json(s3_key,version_id=version_id)
            return data

    def s3_file_delete(self, s3_key):
        kwargs = dict(bucket = self.s3_bucket(),
                      key    = s3_key          )
        return self.s3().file_delete(**kwargs)

    def s3_file_exists(self, s3_key):
        bucket = self.s3_bucket()
        return self.s3().file_exists(bucket, s3_key)

    def s3_file_info(self, s3_key):
        return self.s3().file_details(self.s3_bucket(), s3_key)

    def s3_file_metadata(self, s3_key):
        return self.s3().file_metadata(self.s3_bucket(), s3_key)

    def s3_file_set_metadata(self, s3_key, metadata):
        return self.s3().file_metadata_update(self.s3_bucket(), s3_key, metadata)

    def s3_files_delete(self, s3_keys):                             # Delete multiple S3 files, returning True only if all deletions succeed
        result = True
        for s3_key in s3_keys:
            if not self.s3_file_delete(s3_key):
                result = False
        return result

    def s3_folder_contents(self, folder, return_full_path=False):
        return self.s3().folder_contents(s3_bucket=self.s3_bucket(), parent_folder=folder, return_full_path=return_full_path)

    def s3_folder_files(self, folder='', return_full_path=False, include_sub_folders=False):
        if include_sub_folders:
            return self.s3().find_files(bucket=self.s3_bucket(), prefix=folder)
        else:
            return self.s3().folder_files(s3_bucket=self.s3_bucket(), parent_folder=folder, return_full_path=return_full_path)

    def s3_folder_files__all(self, folder='', full_path=True):                                      # Get all files in a folder, with option to return full paths or relative paths
        all_files = self.s3().find_files(bucket=self.s3_bucket(), prefix=folder)
        if full_path:
            return all_files
        else:
            if folder:
                return [file.replace(folder, '')[1:] for file in all_files]
        return []


    def s3_folder_list(self, folder='', return_full_path=False):
        return self.s3().folder_list(s3_bucket=self.s3_bucket(), parent_folder=folder, return_full_path=return_full_path)

    def s3_save_bytes(self,data, s3_key, metadata=None ):
        kwargs = dict(bucket   = self.s3_bucket(),
                      key       = s3_key        ,
                      file_body = data          ,
                      metadata  = metadata)
        return self.s3().file_upload_from_bytes(**kwargs)

    def s3_save_data(self, data, s3_key, metadata=None):
        from osbot_utils.utils.Json import json_dumps, json_to_gz

        if self.save_as_gz:
            data      = json_to_gz(data)
        kwargs = dict(bucket=self.s3_bucket(), key=s3_key)
        if type(data) == bytes:
            kwargs['file_body'] = data
            kwargs['metadata' ] = metadata
            return self.s3().file_upload_from_bytes(**kwargs)
        else:
            data_as_str = json_dumps(data)
            kwargs["file_contents"] = data_as_str                   # todo: add support for capturing metadata
            return self.s3().file_create_from_string(**kwargs)

    # todo: refactor these s3_temp_folder__pre_signed_urls_* into a separate class (focused on pre_signed_urls)
    def s3_temp_folder__pre_signed_urls_for_object(self, source='NA', reason='NA', who='NA', expiration=3600):
        from osbot_utils.utils.Misc import random_guid, timestamp_utc_now

        s3_bucket          = self.s3_bucket__temp_data()
        s3_temp_folder     = self.s3_folder_temp_file_uploads()
        s3_object_name     = random_guid()
        s3_key             = f'{s3_temp_folder}/{s3_object_name}'
        pre_signed_url__get = self.s3_temp_folder__pre_signed_url(s3_bucket, s3_key, operation='get_object', expiration=expiration)
        pre_signed_url__put = self.s3_temp_folder__pre_signed_url(s3_bucket, s3_key, operation='put_object', expiration=expiration)
        pre_signed_data = dict(pre_signed_url__get = pre_signed_url__get ,
                               pre_signed_url__put = pre_signed_url__put ,
                               reason              = reason              ,
                               timestamp           = timestamp_utc_now() ,
                               source              = source              ,
                               who                 = who                 )
        return pre_signed_data

    def s3_temp_folder__pre_signed_url(self, s3_bucket, s3_key, operation,expiration=3600):
        create_kwargs = dict(bucket_name=s3_bucket,
                             object_name=s3_key,
                             operation=operation,
                             expiration=expiration)
        pre_signed_url = self.s3().create_pre_signed_url(**create_kwargs)
        return pre_signed_url

    def s3_temp_folder__pre_signed_url__download_string(self, pre_signed_url):
        import requests
        response = requests.get(pre_signed_url)
        if response.status_code == 200:
            return response.text
        #pprint(response)                   # todo: add a better way to handle the we dont' get an 200 status_code

    def s3_temp_folder__pre_signed_url__upload_string(self, pre_signed_url, file_contents):
        import requests

        response = requests.put(pre_signed_url, data=file_contents)
        if response.status_code == 200:
            return True
        else:
            return False

    def s3_folder_temp_file_uploads(self):
        return S3_FOLDER__TEMP_FILE_UPLOADS

    # setup and restore

    def bucket_delete(self):
        bucket_name = self.s3_bucket()
        return self.s3().bucket_delete(bucket_name)

    def bucket_delete_all_files(self):
        return self.s3().bucket_delete_all_files(self.s3_bucket())

    def bucket_exists(self):
        bucket_name = self.s3_bucket()
        return self.s3().bucket_exists(bucket_name)

    def setup(self):

        from osbot_aws.AWS_Config  import aws_config
        from osbot_utils.utils.Dev import pformat

        bucket_name = self.s3_bucket()

        kwargs = dict(bucket     = bucket_name              ,
                      region     = aws_config.region_name() ,
                      versioning = self.bucket_versioning   )

        if self.s3().bucket_not_exists(bucket_name):
            result = self.s3().bucket_create(**kwargs)
            if result.get('status') != 'ok':
                message = f"""Catastrophic error: Failed to create bucket:
                
                            { pformat(self.json()) }
                            
                            { pformat(result) }
                            """
                raise Exception(message)                                                                # todo: find a better way to handle these 'catastrophic' errors
            if self.bucket_versioning:                                                                  # if bucket versioning is enabled
                self.s3().bucket_versioning__enable(bucket_name)                                        #    configure it
            assert result.get('status') == 'ok'



        return self

    def using_minio(self):
        from osbot_aws.aws.s3.S3__Minio import DEFAULT__MINIO__SERVER

        return self.use_minio and self.s3().client().meta.endpoint_url == DEFAULT__MINIO__SERVER

    def using_local_stack(self):
        return self.s3().client().meta.endpoint_url == DEFAULT__LOCAL_STACK__TARGET_SERVER