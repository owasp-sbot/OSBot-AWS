import sys ;
from time import sleep

from osbot_aws.apis.Logs import Logs

sys.path.append('..')
from unittest import TestCase

from pbx_gs_python_utils.utils.Dev import Dev
from osbot_aws.apis.test_helpers.Temp_Lambda import Temp_Lambda
from osbot_aws.apis.Lambda import Lambda
from osbot_aws.apis.Lambdas import Lambdas


class test_Lambdas_Creation(TestCase):

    def test_lambdas_cloud_watch_logs(self):
        with Temp_Lambda() as _:
            assert _.invoke() == 'hello None'
            log_name = '/aws/lambda/{0}'.format(_.name)
            logs     = Logs(log_group_name=log_name)
            assert logs.group_exists() is True
            logs.stream_name  = logs.streams()[0].get('logStreamName')

            sleep(0.5)                      # wait for logs to be updated
            messages = logs.messages()
            assert len(messages) > 0
            assert 'START RequestId: ' in messages.pop()





    def test_delete_temp_lambdas(self):
        names = [name for name in Lambdas().list().keys() if (name.startswith('temp_lambda_'))]
        for name in names:
            assert Lambda(name).delete() is True

        names = [name for name in Lambdas().list().keys() if (name.startswith('temp_lambda_'))]
        assert names == []