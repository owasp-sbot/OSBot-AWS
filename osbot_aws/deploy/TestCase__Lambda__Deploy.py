from typing                             import Callable
from osbot_aws.aws.lambda_.Lambda              import Lambda
from osbot_aws.deploy.Deploy_Lambda     import Deploy_Lambda
from osbot_aws.helpers.Lambda_Upload_Package import Lambda_Upload_Package
from osbot_aws.testing.TestCase__Lambda import TestCase__Lambda


class TestCase__Lambda__Deploy(TestCase__Lambda):
    aws_lambda    : Lambda
    handler       : Callable
    deploy_lambda : Deploy_Lambda

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.deploy_lambda    = Deploy_Lambda(cls.handler)
        cls.aws_lambda       = cls.deploy_lambda.lambda_function()
        cls.aws_lambda.client = cls.client__lambda                          # need to replace this so that it uses the classes that have
        cls.aws_lambda.s3     = cls.type_S3                                 # the temp credentials

    def deploy(self):
        return self.deploy_lambda.update()

    def invoke(self, payload):
        return self.deploy_lambda.invoke(payload)

    def invoke_return_logs(self, payload):
        return self.deploy_lambda.invoke_return_logs(payload)

    def upload_dependencies_to_s3(self, dependencies):
        lambda_upload_package = Lambda_Upload_Package()
        lambda_upload_package.dependencies.s3 = self.type_S3
        lambda_upload_package.upload_to_s3(dependencies)