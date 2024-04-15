from unittest import TestCase

from osbot_aws.aws.boto3.Cache_Boto3_Requests import Cache_Boto3_Requests


class test_Cache_Boto3_Requests(TestCase):
    cache_boto3_requests : Cache_Boto3_Requests

    @classmethod
    def setUpClass(cls):
        cache_boto3_requests: Cache_Boto3_Requests