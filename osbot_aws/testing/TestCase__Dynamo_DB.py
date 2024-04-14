from unittest import TestCase
from osbot_aws.aws.dynamo_db.Dynamo_DB import Dynamo_DB
from osbot_aws.aws.dynamo_db.Dynamo_DB__with_temp_role import Dynamo_DB__with_temp_role


class TestCase__Dynamo_DB(TestCase):
    dynamo_db   : Dynamo_DB

    @classmethod
    def setUpClass(cls):
        cls.dynamo_db = Dynamo_DB__with_temp_role()

    @classmethod
    def tearDownClass(cls):
        pass