from unittest import TestCase

from osbot_aws.aws.apigateway.API_Gateway_V2 import API_Gateway_V2
from osbot_aws.aws.apigateway.API_Gateway_V2__with_temp_role import API_Gateway_V2__with_temp_role


class TestCase__API_Gateway_V2(TestCase):
    api_gateway_v2  : API_Gateway_V2
    reset_iam_creds : bool = False

    @classmethod
    def setUpClass(cls):
        cls.api_gateway_v2 = API_Gateway_V2__with_temp_role()
        if cls.reset_iam_creds:
            cls.api_gateway_v2.temp_role__iam_reset_credentials()


    @classmethod
    def tearDownClass(cls):
        pass