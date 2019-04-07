import sys ; sys.path.append('..')
from unittest import TestCase

from osbot_aws.apis.Lambda import Lambda
from osbot_aws.apis.Lambdas import Lambdas


class test_Lambdas_Creation(TestCase):


    def test_delete_temp_lambdas(self):
        names = [name for name in Lambdas().list().keys() if (name.startswith('temp_lambda_'))]
        for name in names:
            assert Lambda(name).delete() is True

        names = [name for name in Lambdas().list().keys() if (name.startswith('temp_lambda_'))]
        assert names == []