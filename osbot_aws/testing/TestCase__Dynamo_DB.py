from unittest import TestCase
from osbot_aws.aws.dynamo_db.Dynamo_DB import Dynamo_DB
from osbot_aws.aws.dynamo_db.Dynamo_DB__with_temp_role import Dynamo_DB__with_temp_role


class TestCase__Dynamo_DB(TestCase):
    dynamo_db      : Dynamo_DB
    reset_iam_creds: bool = False

    @classmethod
    def setUpClass(cls):
        cls.dynamo_db = Dynamo_DB__with_temp_role()
        if cls.reset_iam_creds:
            cls.dynamo_db.temp_role__iam_reset_credentials()


    @classmethod
    def tearDownClass(cls):
        pass