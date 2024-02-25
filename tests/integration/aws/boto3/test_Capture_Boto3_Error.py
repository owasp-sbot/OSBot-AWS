from io import StringIO
from unittest import TestCase
from unittest.mock import patch

import botocore

from osbot_aws.aws.boto3.Capture_Boto3_Error import capture_boto3_error
from botocore.exceptions import ClientError, ParamValidationError


class test_Capture_Boto3_Error(TestCase):

    @patch('sys.stdout', new_callable=StringIO)
    def test_decorator__for_validation_exception(self, sys_stdout):
        expected_output = ('\n'
                          '\n'
                          "'****** BOTO3 ERROR DETECTED ******'\n"
                          '\n'
                          "{ 'details': { 'detail_message': 'max_tokens_to_sample: range: "
                          "1..1,000,000',\n"
                          "               'operation': 'InvokeModel'},\n"
                          "  'error_code': 'ValidationException',\n"
                          "  'error_message': 'An error occurred (ValidationException) when calling the "
                          "'\n"
                          "                   'InvokeModel operation: max_tokens_to_sample: range: '\n"
                          "                   '1..1,000,000'}\n")
        error_response = {'Error': { 'Code': 'ValidationException',
                                      'Message': "An error occurred (ValidationException) when calling the InvokeModel operation: max_tokens_to_sample: range: 1..1,000,000"}}
        operation_name = 'InvokeModel'
        @capture_boto3_error
        def raise_client_error():
            raise ClientError(error_response=error_response, operation_name=operation_name)
        raise_client_error()

        assert sys_stdout.getvalue() == expected_output

    @patch('sys.stdout', new_callable=StringIO)
    def test_decorator_for_param_validation_error(self, sys_stdout):
        expected_output =  ('\n'
                            '\n'
                            "'****** BOTO3 ERROR DETECTED ******'\n"
                            '\n'
                            "{ 'error_code': 'ParamValidationError',\n"
                            "  'error_message': 'Parameter validation failed:\\n'\n"
                            "                   'Parameter validation failed: Invalid type for parameter "
                            "'\n"
                            '                   "body, value: None, type: <class \'NoneType\'>, valid '
                            'types: "\n'
                            '                   "<class \'bytes\'>, <class \'bytearray\'>, file-like '
                            'object"}\n')

        @capture_boto3_error
        def raise_param_validation_error():
            raise ParamValidationError(report="Parameter validation failed: Invalid type for parameter body, value: None, type: <class 'NoneType'>, valid types: <class 'bytes'>, <class 'bytearray'>, file-like object")

        raise_param_validation_error()

        self.assertEqual(sys_stdout.getvalue(), expected_output)