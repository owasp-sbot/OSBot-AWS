from unittest                                       import TestCase
from unittest.mock                                  import call, patch
from osbot_aws.apis.S3                              import S3
from osbot_aws.apis.Lambda                          import Lambda
from osbot_aws.aws.boto3.View_Boto3_Rest_Calls      import print_boto3_calls


class test_View_Boto3_Rest_Calls(TestCase):

    @patch('builtins.print')
    def test__enter__exit(self, builtins_print):

        @print_boto3_calls
        def make_some_aws_calls():
            Lambda().functions()
            S3().buckets()

        make_some_aws_calls()

        assert builtins_print.call_count == 12

        calls = builtins_print.mock_calls
        assert calls[0] == call()
        assert calls[1] == call()
        assert calls[2] == call('|-------------------------------------------------------|')
        assert calls[3] == call('| BOTO3 REST calls (via BaseClient._make_api_call)      |')
        assert calls[4] == call('|-------------------------------------------------------|')
        assert calls[5] == call('| #  | Method                 | Duration | Return Value |')
        assert calls[6] == call('|-------------------------------------------------------|')
        assert "|  0 | ListFunctions          |   " in str(calls[7])
        assert "| {'Functions': [{'FunctionName': " in str(calls[7])
        assert "|  1 | ListBuckets            |   " in str(calls[8])
        assert "ms | {'Buckets': [{'Name': '"       in str(calls[8])
        assert calls[9] == call('|-------------------------------------------------------|')
        assert 'Total Duration:' in str(calls[10])
        assert 'Total calls:'    in str(calls[10])
        assert calls[11] == call('|-------------------------------------------------------|')
