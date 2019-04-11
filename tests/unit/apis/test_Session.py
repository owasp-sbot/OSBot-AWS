from unittest import TestCase

import boto3
from botocore.session import get_session
from pbx_gs_python_utils.utils.Dev import Dev

from osbot_aws.Globals import Globals
from osbot_aws.apis.Session import Session


class test_Session(TestCase):

    def setUp(self):
        self.session = Session()

    def test_client(self):
        assert self.session.client('aaaa') is None
        assert type(self.session.client('s3')).__name__ == 'S3'

    def test_client_boto(self):
        assert "Unknown service: 'aaaa'. Valid service names are:" in self.session.client_boto3('aaaa').get('data')
        Globals.aws_session_profile_name = 'bad_profile'
        assert type(self.session.client_boto3('s3').get('client')).__name__ == 'S3'
        Globals.aws_session_profile_name = 'default'

