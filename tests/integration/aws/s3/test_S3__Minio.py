from unittest                           import TestCase
from osbot_aws.aws.s3.S3                import S3
from osbot_aws.aws.s3.S3__Minio         import S3__Minio, DEFAULT__MINIO__SERVER
from osbot_utils.testing.Hook_Method    import Hook_Method
from osbot_utils.utils.Misc             import list_set


class test_Minio_As_S3(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.minio_as_s3 = S3__Minio()

    def test_connect_to_server(self):
        with self.minio_as_s3 as _:
            assert _.connect_to_server() == { 'data'    : None                                      ,
                                              'error'   : None                                      ,
                                              'message' : 'MinIO console is accessible on port 9001',
                                              'status'  : 'ok'                                      }
            assert _.server_online    () is True

    def test_s3_client(self):
        with self.minio_as_s3 as _:
            s3  = _.s3_client()
            assert s3.meta.service_model.service_name == 's3'
            assert list_set(s3.list_buckets()) == ['Buckets', 'Owner', 'ResponseMetadata']


    def test_using_hook_method(self):
        hook_method =  Hook_Method(S3, "client")
        hook_method.mock_call = test_Minio_As_S3.s3_minio__s3_client
        hook_method.wrap()
        assert S3().client().meta.endpoint_url == DEFAULT__MINIO__SERVER                        # confirm it is minio
        hook_method.unwrap()

        with Hook_Method(S3, "client") as s3_hook:
            s3_hook.mock_call = test_Minio_As_S3.s3_minio__s3_client
            assert S3().client().meta.endpoint_url == DEFAULT__MINIO__SERVER                    # confirm it is minio

    def s3_minio__s3_client(self):
        return S3__Minio().s3_client()