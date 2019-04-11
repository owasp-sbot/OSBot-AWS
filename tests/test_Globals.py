import sys; sys.path.append('..')
from unittest import TestCase

from osbot_aws.Globals import Globals


class test_Globals(TestCase):

    def test_static_values(self):
        assert Globals.aws_session_profile_name == 'default'
        assert Globals.aws_session_region_name  == 'eu-west-2'
        assert Globals.lambda_s3_bucket         == 'gs-lambda-tests'