from unittest import TestCase

import botocore

from osbot_aws.aws.boto3.Capture_Boto3_Error import capture_boto3_error

from botocore.exceptions import ClientError

class test_Capture_Boto3_Error(TestCase):

    @capture_boto3_error
    def test_decorator(self):
        raise ClientError({'Error': { 'Code': 'ValidationException',
                                                          'Message': "An error occurred (ValidationException) when calling the InvokeModel operation: max_tokens_to_sample: range: 1..1,000,000"}},
                                              'InvokeModel' )