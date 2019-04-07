from unittest import TestCase

from pbx_gs_python_utils.utils.Dev import Dev

from osbot_aws.apis.Lambda import Lambda
from osbot_aws.apis.Lambdas import Lambdas


class test_Lambdas_Creation(TestCase):

    # def test_create_delete_exists_invoke(self):
    #
    #     assert self.test_lambda.delete(             ) == self.test_lambda  # delete function
    #     assert self.test_lambda.exists(             ) is False             # confirm it doesn't exist
    #     assert self.test_lambda.create(             ) == self.test_lambda  # confirm create returns test_lambda object
    #     assert self.test_lambda.exists(             ) is True              # confirm it now exists
    #
    #     path = Files.path_combine('.', '../../..')
    #     self.test_lambda.update_with_src(path)
    #
    #     assert self.test_lambda.invoke(             ) == "hello None"      # invoke with no params
    #     assert self.test_lambda.invoke({'name':'AA'}) == "hello AA"        # invoke with an param
    #     assert self.test_lambda.delete(             ) == self.test_lambda  # delete it
    #     assert self.test_lambda.exists(             ) is False             # confirm deletion


    def test_delete_temp_lambdas(self):
        names = [name for name in Lambdas().list().keys() if (name.startswith('temp_lambda_'))]
        assert names == []
        #for name in names:
        #    assert Lambda(name).delete() is True