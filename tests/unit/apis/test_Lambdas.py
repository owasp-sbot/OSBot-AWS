from unittest import TestCase

from pbx_gs_python_utils.utils.Dev import Dev

from osbot_aws.apis.Lambdas import Lambdas


class Test_Lambdas(TestCase):

    def test_list(self):
        all_lambdas = list(Lambdas().list().values())
        assert len(all_lambdas) > 0
        assert set(all_lambdas.pop(0)) == { 'CodeSha256','CodeSize','Description','FunctionArn','FunctionName','Handler','LastModified','MemorySize','RevisionId','Role','Runtime','Timeout','TracingConfig','Version','VpcConfig'}
