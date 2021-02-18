import os
from unittest                               import TestCase
from osbot_aws.AWS_Config                   import AWS_Config
from osbot_aws.Dependencies                 import pip_install_dependency, upload_dependency
from osbot_aws.apis.S3                      import S3
from osbot_aws.apis.STS                     import STS
from osbot_aws.helpers.Rest_API             import Rest_API
from osbot_aws.lambdas.dev.fast_api_sample  import run
from osbot_aws.apis.Lambda                  import Lambda
from osbot_aws.deploy.Deploy_Lambda         import Deploy_Lambda
from osbot_aws.lambdas.dev.fastapi.app.main import app
from fastapi.testclient                     import TestClient

client = TestClient(app)

class test_fast_api_sample(TestCase):
    lambda_ : Lambda
    test_rest_api_name = 'temp-unit-test-fast-api'

    @staticmethod
    def check_or_upload_dependency(target):
        """
        Check if the required dependency is present in the configured bucked and if not upload the dependency
        :param target: dependency to upload
        """
        s3 = S3()
        s3_bucket = AWS_Config().lambda_s3_bucket()
        s3_key = 'lambdas-dependencies/{0}.zip'.format(target)
        if s3.file_exists(s3_bucket, s3_key) is False:
            assert pip_install_dependency(target) is True
            assert upload_dependency(target)      is True

    @staticmethod
    def setup_test_environment__Rest_API(cls):
        rest_api = Rest_API(cls.test_rest_api_name).create()
        assert  rest_api.exists()

    @staticmethod
    def teardown_test_environment__Rest_API(cls):
        rest_api = Rest_API(cls.test_rest_api_name)
        assert rest_api.delete().not_exists()

    @staticmethod
    def get_environment_variable():
        """
        This is needed by the lambda function to pull required dependencies
        :return: env variable
        """
        vars_to_add   = ['OSBOT_LAMBDA_S3_BUCKET']
        env_variables = {}
        for var_to_add in vars_to_add:
            env_variables[var_to_add] = os.environ.get(var_to_add)
        return env_variables

    @classmethod
    def setUpClass(cls) -> None:
        STS().check_current_session_credentials()
        cls.handler                                   = run
        cls.deploy                                    = Deploy_Lambda(cls.handler)
        cls.deploy.package.add_osbot_utils()                                                   # Add OSbots Util Dependency
        cls.lambda_name                               = cls.deploy.lambda_name()
        cls.lambda_                                   = Lambda(name= cls.lambda_name)

        assert cls.deploy.deploy()                    is True
        assert cls.lambda_.exists()                   is True

        cls.deploy.package.aws_lambda.env_variables   = cls.get_environment_variable()         # Configure Environment Variable needed by the Lambda
        cls.deploy.package.aws_lambda.update_lambda_configuration()
        cls.setup_test_environment__Rest_API(cls)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.teardown_test_environment__Rest_API(cls)
        assert cls.lambda_.delete(delete_log_group=False) is True

    def setUp(self):
        super().setUp()
        self.rest_api = Rest_API(self.test_rest_api_name).create()

    def test_check_or_upload_dependency(self):
        # Ensure that all the required dependencies are available in configured S3 bucket
        dependencies = 'mangum,fastapi'
        for target in dependencies.split(','):
            self.check_or_upload_dependency(target)

    def test_invoke_api_directly(self):
        response = client.get("/")
        assert response.status_code    ==  200
        assert response.json()         == {"message": "Hello from FastApi"}

        response = client.get("/api/v1/users/")
        assert response.status_code    ==  200
        assert response.json()         == {"message": "Users!"}

        response = client.get("/api/v1/users/user1")
        assert response.status_code    ==  200
        assert response.json()         == {"message": "this is user1!"}

    def test_setup_lambda__api_gateway(self):
        parent_id   = self.rest_api.resource_id('/')
        self.result = self.rest_api.api_gateway.resource_create(self.rest_api.id(),parent_id,'{proxy+}')
        self.result = self.rest_api.add_method_lambda('/'        , 'ANY', self.lambda_.name)
        self.result = self.rest_api.add_method_lambda('/{proxy+}', 'ANY', self.lambda_.name)
        self.rest_api.deploy()

        response                        = self.rest_api.test_method('/', 'GET')
        assert response.get('status'                                     ) == 200
        assert response.get('body'                                       ) == '{"message":"Hello from FastApi"}'
        #response                                                          = self.rest_api.test_method('/api/v1/users/', 'GET') # FixMe this doesn't work when we configure resource as /{proxy+}
        assert self.rest_api.invoke_GET('/api/v1/users/'                 ) == '{"message":"Users!"}'
        assert self.rest_api.invoke_GET('/api/v1/users/user1'            ) == '{"message":"this is user1!"}'