from unittest import TestCase

from pbx_gs_python_utils.utils.Misc import Misc

from osbot_aws.helpers.Lambda_Package import Lambda_Package


class test_Lambda_Package(TestCase):
    def setUp(self):
        name = "temp_lambda_{0}".format(Misc.random_string_and_numbers())
        self.package = Lambda_Package(name)

    def test__init__(self):
        assert type(self.package._lambda).__name__ == 'Lambda'