from unittest import TestCase

from osbot_aws.apis.Lambda                        import Lambda
from osbot_aws.apis.S3                            import S3
from osbot_aws.aws.dynamo_db.Dynamo_DB            import Dynamo_DB
from osbot_aws.aws.dynamo_db.Dynamo_DB__with_temp_role import Dynamo_DB__with_temp_role
from osbot_aws.aws.lambda_.Lambda__with_temp_role import Lambda__with_temp_role
from osbot_aws.aws.s3.S3__with_temp_role          import S3__with_temp_role
from osbot_aws.testing.Pytest import skip_pytest___aws_pytest_user_name__is_not_set
from osbot_aws.testing.TestCase__Boto3_Cache import TestCase__Boto3_Cache
from osbot_utils.base_classes.Type_Safe import Type_Safe
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.utils.Misc import random_text


class TestCase__S3(TestCase__Boto3_Cache, Type_Safe):
    type_S3          : type
    client__s3       : object
    s3               : S3
    reset_iam_creds : bool = False

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        skip_pytest___aws_pytest_user_name__is_not_set()
        cls.type_S3           = S3__with_temp_role
        cls.s3                = cls.type_S3()
        cls.client__s3        = cls.s3.client

        if cls.reset_iam_creds:
            cls.s3       .temp_role__iam_reset_credentials()