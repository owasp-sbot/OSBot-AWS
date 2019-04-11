import sys ; sys.path.append('..')

from osbot_aws.Globals import Globals

import unittest
from osbot_aws.apis.test_helpers.Temp_Lambda import Temp_Lambda

from osbot_aws.apis.test_helpers.Temp_Aws_Roles import Temp_Aws_Roles

from osbot_aws.apis.IAM import IAM



#import unittest
from pbx_gs_python_utils.utils.Dev  import Dev
from unittest                       import TestCase
from osbot_aws.apis.Lambda          import Lambda

# these tests require lambdas to already exist in AWS
class test_Lambdas_Invoke(TestCase):

    def test_dev_hello_world(self):
        assert Lambda('dev_hello_world').invoke() == 'hello None'

    def test_lambdas_gsbot_gsbot_graph(self):
        assert Lambda('lambdas_gsbot_gsbot_graph').invoke_raw().get('status') == 'ok'


    @unittest.skip
    def test_run_lambdas_in_multiple_accounts(self):
        Globals.aws_session_profile_name = 'gs-detect-aws'
        Globals.lambda_s3_bucket         = 'gs-detect-lambda'
        with Temp_Lambda() as _:
            _.invoke_raw().get('status') == 'ok'

        Globals.aws_session_profile_name = 'default'


