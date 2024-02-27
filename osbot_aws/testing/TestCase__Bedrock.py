from unittest import TestCase

from osbot_aws.aws.bedrock.Bedrock import Bedrock
from osbot_aws.aws.bedrock.Bedrock__with_temp_role import Bedrock__with_temp_role


class TestCase__Bedrock(TestCase):
    bedrock     : Bedrock
    region_name : str


    @classmethod
    def setUpClass(cls):
        cls.region_name = 'us-east-1'
        cls.bedrock = Bedrock__with_temp_role(region_name=cls.region_name)


    @classmethod
    def tearDownClass(cls):
        pass