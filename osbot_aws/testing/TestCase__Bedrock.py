from unittest import TestCase

import pytest

from osbot_aws.aws.bedrock.Bedrock                  import Bedrock
from osbot_aws.aws.bedrock.Bedrock__with_temp_role  import Bedrock__with_temp_role
from osbot_aws.aws.bedrock.cache.Bedrock__Cache     import Bedrock__Cache
from osbot_aws.testing.Pytest                       import skip_pytest___aws_pytest_user_name__is_not_set
from osbot_utils.utils.Env                          import in_github_action


class TestCase__Bedrock(TestCase):
    bedrock     : Bedrock
    region_name : str
    cache       : Bedrock__Cache


    @classmethod
    def setUpClass(cls):
        skip_pytest___aws_pytest_user_name__is_not_set()
        if in_github_action():              # skipping all tests in GH actions, since there is no cache in there are we are just having cost with no value                             # disabling Bedrock tests in GitHub actions since they are not 100% deterministic
            pytest.skip()
        cls.region_name = 'us-east-1'
        cls.bedrock = Bedrock__with_temp_role(region_name=cls.region_name)
        cls.cache   = cls.bedrock.bedrock_cache

    @classmethod
    def tearDownClass(cls):
        pass
