from unittest import TestCase

from osbot_utils.utils.Http import current_host_online

# in addition to checking if we are online adding a test in the root of the tests/integrations
#    folder also helps with the UX in pycharm since we have a right click option to run all tests in this folder (recursively)
class test_integration(TestCase):

    def test__confirm_we_are_online(self):
        assert current_host_online() is True
