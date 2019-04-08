import sys ; sys.path.append('..')
from unittest import TestCase

from pbx_gs_python_utils.utils.Dev import Dev
from osbot_aws.apis.test_helpers.Temp_Lambda import Temp_Lambda
from osbot_aws.apis.Lambda import Lambda
from osbot_aws.apis.Lambdas import Lambdas


class test_Lambdas_Creation(TestCase):

    def test_lambdas_cloud_watch_logs(self):
        with Temp_Lambda() as _:
            _.delete_on_exit = False
            Dev.pprint(_.create_log)
            result = _.invoke_raw()
            #Dev.pprint(result)

    def test_delete_temp_lambdas(self):
        names = [name for name in Lambdas().list().keys() if (name.startswith('temp_lambda_'))]
        for name in names:
            assert Lambda(name).delete() is True

        names = [name for name in Lambdas().list().keys() if (name.startswith('temp_lambda_'))]
        assert names == []