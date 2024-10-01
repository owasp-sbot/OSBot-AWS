from unittest                                           import TestCase
from osbot_aws.aws.lambda_.Lambda                       import Lambda
from osbot_aws.aws.s3.S3                                import S3
from osbot_aws.aws.dynamo_db.Dynamo_DB                  import Dynamo_DB
from osbot_aws.aws.dynamo_db.Dynamo_DB__with_temp_role  import Dynamo_DB__with_temp_role
from osbot_aws.aws.lambda_.Lambda__with_temp_role       import Lambda__with_temp_role
from osbot_aws.aws.s3.S3__with_temp_role                import S3__with_temp_role
from osbot_aws.testing.Pytest                           import skip_pytest___aws_pytest_user_name__is_not_set


class TestCase__Lambda(TestCase):
    client__dynamo_db: object
    client__lambda   : object
    client__s3       : object
    type_Dynamo_DB   : type
    type_Lambda      : type
    type_S3          : type
    dynamo_db        : Dynamo_DB
    lambda_          : Lambda
    s3               : S3
    reset_iam_creds : bool = False

    @classmethod
    def setUpClass(cls):
        skip_pytest___aws_pytest_user_name__is_not_set()
        cls.type_Dynamo_DB    = Dynamo_DB__with_temp_role
        cls.type_Lambda       = Lambda__with_temp_role
        cls.type_S3           = S3__with_temp_role
        cls.dynamo_db         = cls.type_Dynamo_DB()
        cls.lambda_           = cls.type_Lambda()
        cls.s3                = cls.type_S3()
        cls.client__dynamo_db = cls.dynamo_db.client
        cls.client__lambda    = cls.lambda_  .client
        cls.client__s3        = cls.s3       .client

        if cls.reset_iam_creds:
            cls.dynamo_db.temp_role__iam_reset_credentials()
            cls.lambda_  .temp_role__iam_reset_credentials()
            cls.s3       .temp_role__iam_reset_credentials()

    @classmethod
    def tearDownClass(cls):
        pass