from unittest import TestCase
from osbot_aws.aws.dynamo_db.Dynamo_DB import Dynamo_DB
from osbot_aws.aws.dynamo_db.Dynamo_DB__with_temp_role import Dynamo_DB__with_temp_role
from osbot_aws.testing.Pytest import skip_pytest___aws_pytest_user_name__is_not_set


class TestCase__Dynamo_DB(TestCase):
    dynamo_db      : Dynamo_DB
    reset_iam_creds: bool = False

    @classmethod
    def setUpClass(cls):
        skip_pytest___aws_pytest_user_name__is_not_set()
        cls.dynamo_db = Dynamo_DB__with_temp_role()
        if cls.reset_iam_creds:
            cls.dynamo_db.temp_role__iam_reset_credentials()


    @classmethod
    def tearDownClass(cls):
        pass