from osbot_aws.testing.TestCase__S3__Temp_DB import TestCase__S3__Temp_DB
from osbot_utils.utils.Misc                  import random_text
from osbot_aws.utils.AWS_Sanitization        import str_to_valid_s3_bucket_name
from osbot_utils.utils.Objects               import __, dict_to_obj
from osbot_aws.AWS_Config                    import aws_config
from osbot_aws.aws.s3.S3__DB_Base            import S3_DB_BASE__BUCKET_NAME__PREFIX, S3_DB_BASE__BUCKET_NAME__SUFFIX, S3__DB_Base


class test_S3__DB__Base(TestCase__S3__Temp_DB):

    def test___init__(self):
        with self.s3_db_base as _:
            assert type(_) is S3__DB_Base
            assert _.using_local_stack() is True
            assert _.obj()               == __(use_minio                      = False            ,
                                               bucket_name__suffix            = 'osbot-aws'      ,
                                               bucket_name__prefix            = 'unknown-service',
                                               bucket_name__insert_account_id = True             ,
                                               bucket_versioning              = True             ,
                                               save_as_gz                     = False            ,
                                               server_name                    = 'unknown-server' ,
                                               session_kwargs__s3             = __(service_name          = 's3',
                                                                                   aws_access_key_id     = None,
                                                                                   aws_secret_access_key = None,
                                                                                   endpoint_url          = None,
                                                                                   region_name           = None))

    def test_s3(self):
        with self.s3_db_base as _:
            assert _.s3().bucket_exists(_.s3_bucket()) is True
            assert _.s3().client().meta.endpoint_url == 'http://localhost:4566'

    # def test_s3__minio(self):
    #     with self.s3_db_base as _:
    #         assert _.s3().bucket_exists(_.s3_bucket()) is True
    #     region_name                   = aws_config.region_name()
    #     expected__s3__endpoint_url    = f'https://s3.{region_name}.amazonaws.com'
    #     expected__minio__endpoint_url = DEFAULT__MINIO__SERVER
    #
    #     expected__s3_aws = __(tmp_file_folder='s3_temp_files',
    #                          use_threads=True,
    #                          session_kwargs__s3=__(service_name='s3',
    #                                                aws_access_key_id=None,
    #                                                aws_secret_access_key=None,
    #                                                endpoint_url=None,
    #                                                region_name=None))
    #     expected__minio  = __(tmp_file_folder='s3_temp_files',
    #                           use_threads=True,
    #                           session_kwargs__s3=__(service_name='s3',
    #                                                 aws_access_key_id=DEFAULT__MINIO__ACCESS_KEY,
    #                                                 aws_secret_access_key=DEFAULT__MINIO__SECRET_KEY,
    #                                                 endpoint_url=DEFAULT__MINIO__SERVER,
    #                                                 region_name=None))
    #     assert self.s3_db_base.use_minio is True               # Check default value of use_minio
    #     assert get_env(ENV_NAME__USE_MINIO_AS_S3) == 'True'     # Check that the env var has not been set
    #     with self.s3_db_base as _:
    #
    #         with Temp_Env_Vars(env_vars={ENV_NAME__USE_MINIO_AS_S3:'False'}):
    #             self.s3_db_base.use_minio = False
    #             s3_a = _.s3(reload_cache=True)
    #             assert get_env(ENV_NAME__USE_MINIO_AS_S3) == 'False'
    #             assert s3_a.obj() == expected__s3_aws
    #             assert s3_a.client().meta.endpoint_url in ['http://localhost:4566',expected__s3__endpoint_url, 'https://s3.amazonaws.com'] # todo: figure out why sometimes (mainly locally we get the s3.amazonaws.com url, instead of the one with the zone) , also debug the use of http://localhost:4566
    #             _.use_minio = True
    #             _.s3(reload_cache=True)
    #         assert get_env(ENV_NAME__USE_MINIO_AS_S3) == 'True'
    #
    #         s3_b = _.s3(reload_cache=True)
    #         assert s3_b.obj() == expected__minio
    #         assert s3_b.client().meta.endpoint_url == expected__minio__endpoint_url
    #
    #         _.use_minio = False
    #         temp_vars = {ENV_NAME__USE_MINIO_AS_S3: 'True'}
    #         with Temp_Env_Vars(env_vars=temp_vars):
    #             s3_d = _.s3(reload_cache=True)
    #             assert s3_d.obj() == expected__minio
    #             assert _.use_minio == True
    #
    #         _.use_minio = False
    #         temp_vars = {ENV_NAME__USE_MINIO_AS_S3: 'False'}
    #         with Temp_Env_Vars(env_vars=temp_vars):
    #             s3_d = _.s3(reload_cache=True)
    #             assert s3_d.obj() == expected__s3_aws
    #             assert _.use_minio == False
    #
    #         _.use_minio = True
    #         _.s3(reload_cache=True)
    #         assert get_env(ENV_NAME__USE_MINIO_AS_S3) == 'True'
    #         assert _.using_minio() is True

    def test_s3_bucket(self):
        with self.s3_db_base as _:
            aws_account_id = aws_config.account_id()
            assert _.s3_bucket() == f"{S3_DB_BASE__BUCKET_NAME__PREFIX}-{aws_account_id}-{S3_DB_BASE__BUCKET_NAME__SUFFIX}"
            assert _.using_local_stack() is True
            assert _.bucket_exists() is True

        with self.s3_db_base as _:
            separator       = '-'
            random_aws_creds = self.random_aws_creds
            account_id        = aws_config.account_id()
            raw_bucket_name_1 = f'{S3_DB_BASE__BUCKET_NAME__PREFIX}-{account_id}{separator}{_.bucket_name__suffix}'
            assert account_id    == random_aws_creds.env_vars.get('AWS_ACCOUNT_ID')
            assert _.s3_bucket() == str_to_valid_s3_bucket_name(raw_bucket_name_1)

            _.bucket_name__prefix = 'abc'
            raw_bucket_name_2     = f'abc{separator}{account_id}{separator}{_.bucket_name__suffix}'
            assert _.s3_bucket(reload_cache=True) == str_to_valid_s3_bucket_name(raw_bucket_name_2)

            _.bucket_name__insert_account_id = False
            raw_bucket_name_3 = f'abc{separator}{_.bucket_name__suffix}'
            assert _.s3_bucket(reload_cache=True) == str_to_valid_s3_bucket_name(raw_bucket_name_3)

            _.bucket_name__suffix = 'zzzzz'
            raw_bucket_name_4 = f'abc{separator}{_.bucket_name__suffix}'
            assert _.s3_bucket(reload_cache=True) == str_to_valid_s3_bucket_name(raw_bucket_name_4)

            _.bucket_name__prefix = ''
            raw_bucket_name_5 = f'{_.bucket_name__suffix}'
            assert _.s3_bucket(reload_cache=True) == str_to_valid_s3_bucket_name(raw_bucket_name_5)

            #restore changed values
            _.bucket_name__suffix = 'osbot-aws'
            _.bucket_name__prefix = 'unknown-service'
            _.bucket_name__insert_account_id = True
            assert _.s3_bucket(reload_cache=True) == f'unknown-service-{account_id}-osbot-aws'


    def test_s3_file_bytes(self):
        target_key = 'an_folder/an_file.gz'
        some_bytes = b"This is some bytes"
        metadata   = { 'some_key': 'some_value'}
        with self.s3_db_base as _:
            file_save_result = _.s3_save_bytes(data=some_bytes, s3_key=target_key, metadata=metadata)
            file_info        = _.s3_file_info(target_key)

            assert file_save_result               is True
            assert dict_to_obj       (file_info ) == __(AcceptRanges         = 'bytes',
                                                        LastModified         = file_info.get('LastModified'),
                                                        ContentLength        = 18,
                                                        ETag                 = '"b14c3dc0c37415cb318873bbfa74488d"',
                                                        ContentType          = 'binary/octet-stream',
                                                        Metadata             = __(created_by='osbot_aws.aws.s3.S3.file_upload_from_bytes',
                                                                                  some_key='some_value'),
                                                        ServerSideEncryption ='AES256',
                                                        VersionId            = file_info.get('VersionId'))
            assert _.s3_file_exists  (target_key) is True
            assert _.s3_file_bytes   (target_key) == some_bytes
            assert _.s3_file_metadata(target_key) == metadata

            assert _.s3_file_delete  (target_key) is True
            assert _.s3_file_exists  (target_key) is False

    def test_s3_temp_folder__pre_signed_urls_for_object(self):
        with self.s3_db_base as _:
            signed_url_data       = dict_to_obj(_.s3_temp_folder__pre_signed_urls_for_object())
            pre_signed_url__put = signed_url_data.pre_signed_url__put
            pre_signed_url__get = signed_url_data.pre_signed_url__get
            file_contents__for_put = random_text("some file contents")

            result = _.s3_temp_folder__pre_signed_url__upload_string(pre_signed_url=pre_signed_url__put,
                                                                        file_contents=file_contents__for_put)
            assert result is True

            file_contents__on_get = _.s3_temp_folder__pre_signed_url__download_string(pre_signed_url=pre_signed_url__get)
            assert file_contents__on_get == file_contents__for_put


