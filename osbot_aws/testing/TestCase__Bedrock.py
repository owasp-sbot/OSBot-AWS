from unittest import TestCase

from osbot_aws.aws.bedrock.Bedrock import Bedrock
from osbot_aws.aws.bedrock.Bedrock__with_temp_role import Bedrock__with_temp_role
from osbot_aws.aws.bedrock.cache.Bedrock__Cache import Bedrock__Cache


class TestCase__Bedrock(TestCase):
    bedrock     : Bedrock
    region_name : str
    cache       : Bedrock__Cache


    @classmethod
    def setUpClass(cls):
        cls.region_name = 'us-east-1'
        cls.bedrock = Bedrock__with_temp_role(region_name=cls.region_name)
        cls.cache   = cls.bedrock.bedrock_cache

    @classmethod
    def tearDownClass(cls):
        pass
