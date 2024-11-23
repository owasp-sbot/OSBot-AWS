from osbot_utils.base_classes.Type_Safe             import Type_Safe
from osbot_utils.decorators.methods.cache_on_self   import cache_on_self

from osbot_aws.aws.session.Session__Kwargs__S3 import Session__Kwargs__S3

ENV_NAME__MINIO__SERVER     = 'MINIO__SERVER'
ENV_NAME__MINIO__ACCESS_KEY = 'MINIO__ACCESS_KEY'
ENV_NAME__MINIO__SECRET_KEY = 'MINIO__SECRET_KEY'

DEFAULT__MINIO__SERVER     = 'http://localhost:9000'
DEFAULT__MINIO__ACCESS_KEY = 'minioadmin'                       # todo: change this to a random value
DEFAULT__MINIO__SECRET_KEY = 'minioadmin'                       #       (from env vars, that are also used by minio docker image)

class S3__Minio(Type_Safe):

    def connect_to_server(self):
        import requests
        from osbot_utils.utils.Status import status_ok, status_error

        try:
            response = requests.get(self.url_server())
            # Check if the status code is 200, indicating MinIO is up and running
            if response.status_code == 200:
                return status_ok(message="MinIO console is accessible on port 9001")
            return status_error(message="Server returned status code {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            return status_error(message=f"Could not connect to MinIO console on port 9001: {e}")

    def connection_details(self):
        from osbot_utils.utils.Env import get_env

        server     = get_env(ENV_NAME__MINIO__SERVER    , DEFAULT__MINIO__SERVER    )
        access_key = get_env(ENV_NAME__MINIO__ACCESS_KEY, DEFAULT__MINIO__ACCESS_KEY)
        secret_key = get_env(ENV_NAME__MINIO__SECRET_KEY, DEFAULT__MINIO__SECRET_KEY)
        return server, access_key, secret_key

    def s3(self):
        from osbot_aws.aws.s3.S3 import S3

        server, aws_access_key_id, aws_secret_access_key = self.connection_details()
        session_kwargs__s3                               = Session__Kwargs__S3(endpoint_url          = server                ,
                                                                              aws_access_key_id     = aws_access_key_id     ,
                                                                              aws_secret_access_key = aws_secret_access_key )
        s3                                               = S3(session_kwargs__s3=session_kwargs__s3)
        return s3

    def s3_client(self):
        import boto3
        from botocore.config import Config

        server, access_key, secret_key = self.connection_details()
        minio_endpoint   = server
        minio_access_key = access_key
        minio_secret_key = secret_key

        # Create a session and S3 client configured to use MinIO
        s3_client = boto3.client('s3',
            endpoint_url          = minio_endpoint                  ,
            aws_access_key_id     = minio_access_key                ,
            aws_secret_access_key = minio_secret_key                ,
            config                = Config(signature_version='s3v4'),
            region_name           = 'us-east-1'                     )
        return s3_client

    @cache_on_self
    def server_online(self):
        return self.connect_to_server().get('status') == 'ok'

    def url_server(self):
        return 'http://localhost:9001'
