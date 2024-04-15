from unittest import TestCase

from osbot_aws.aws.boto3.Cache_Boto3_Requests import Cache_Boto3_Requests


class TestCase__Boto3_Cache(TestCase):
    cache : Cache_Boto3_Requests

    @classmethod
    def setUpClass(cls):
        cls.cache = Cache_Boto3_Requests()
        cls.cache.patch_apply()

    @classmethod
    def tearDownClass(cls):
        cls.cache.patch_restore()
