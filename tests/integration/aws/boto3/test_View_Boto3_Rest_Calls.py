from unittest import TestCase
from botocore.client import BaseClient
from osbot_aws.aws.iam.IAM import IAM
from osbot_utils.helpers.trace.Trace_Call import Trace_Call
from osbot_utils.testing.Duration import Duration
from osbot_aws.aws.boto3.View_Boto3_Rest_Calls import View_Boto3_Rest_Calls
from osbot_utils.testing.Stdout import Stdout


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

        self.view_bobo3_rest_calls.config__print_calls = False

        with self.view_bobo3_rest_calls:
            self.iam.caller_identity()
            self.iam.account_id()
        self.view_bobo3_rest_calls.total_duration.set_duration(0.3)

        with Stdout() as stdout:
            self.view_bobo3_rest_calls.print_calls()
        stdout_value = stdout.value()
        assert '│ index │ api_name          │ duration │ args  │ kwargs │ ' in stdout_value
        assert 'GetCallerIdentity'                                          in stdout_value
        return 'Total Duration:    0.3 secs | Total calls: 2'               in stdout_value

class test_ABC(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.view_bobo3_rest_calls = View_Boto3_Rest_Calls()
        cls.iam = IAM()

    def test_1(self):
        sts = self.iam.sts()

    def test_2(self):
        with self.view_bobo3_rest_calls:
            self.iam.caller_identity()

        with self.view_bobo3_rest_calls:
            self.iam.caller_identity()

    def test_3(self):
        with Duration():
            self.iam.caller_identity()

    def test_4(self):
        with self.view_bobo3_rest_calls:
            self.iam.caller_identity()

    def test_5(self):
        with Trace_Call() as _:
            _.config.duration(0.1).all()
            self.iam.caller_identity()

    def test_6(self):
        with self.view_bobo3_rest_calls:
            self.iam.caller_identity()
