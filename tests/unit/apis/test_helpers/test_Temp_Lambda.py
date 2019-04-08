from unittest import TestCase

from pbx_gs_python_utils.utils.Dev import Dev
from osbot_aws.apis.test_helpers.Temp_Lambda import Temp_Lambda


class test_Temp_Lambda(TestCase):

    def test_simple_execution(self):
        with Temp_Lambda() as _:
            Dev.pprint(_.temp_lambda.name)
            assert _.invoke() == 'hello None'
