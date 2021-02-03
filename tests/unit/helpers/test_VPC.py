from unittest import TestCase

from osbot_aws.apis.test_helpers.Temp_VPC import Temp_VPC


class test_VPC(TestCase):

    def test_using_Temp_VPC(self):
        # this class using VPC for its creation and deleting steps, and if no exceptions are
        # thrown it means that everything went ok
        temp_vpc = Temp_VPC(add_internet_gateway=True, add_route_table=True, add_security_group=True, add_subnet=True)
        with temp_vpc:
             pass