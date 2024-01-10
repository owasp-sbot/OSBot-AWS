from unittest import TestCase

from botocore.client import BaseClient

from osbot_aws.aws.iam.IAM import IAM
from osbot_utils.utils.Dev import pprint

from osbot_utils.testing.Duration import Duration

from osbot_aws.aws.boto3.View_Boto3_Rest_Calls import View_Boto3_Rest_Calls


class test_View_Boto3_Rest_Calls(TestCase):

    def setUp(self):
        self.view_bobo3_rest_calls = View_Boto3_Rest_Calls()
        self.iam = IAM()

    def test___init__(self):
        assert self.view_bobo3_rest_calls.target_module         is BaseClient
        assert self.view_bobo3_rest_calls.target_method         == "_make_api_call"
        assert self.view_bobo3_rest_calls.hook_method           is None
        assert self.view_bobo3_rest_calls.config__print_calls   is True
        assert type(self.view_bobo3_rest_calls.total_duration)  is Duration

    def test___enter__exit__(self):
        with self.view_bobo3_rest_calls as hook_method:
            assert hook_method.target_module is BaseClient
            assert hook_method.target_method == "_make_api_call"
            pprint(hook_method.calls)
            self.iam.caller_identity()
            self.iam.caller_identity()
            self.iam.caller_identity()
        #     assert hook_method.hook_method   is not None
        #     assert hook_method.on_exit_print_calls is True
        #     assert type(hook_method.total_duration) is Duration
        # assert hook_method.hook_method is None