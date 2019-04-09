import sys ; sys.path.append('..')

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