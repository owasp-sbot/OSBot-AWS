from unittest import TestCase

from osbot_aws.helpers.AMI import AMI


class test_AMI(TestCase):

    def setUp(self) -> None:
        self.ami                 = AMI()
        self.current_region_name = self.ami.current_region_name

    def test_amazon_linux_2(self):
        image_name = 'amazon-linux-2'
        assert self.ami.amazon_linux_2() == self.ami.ami_mappings_per_region().get(image_name).get(self.current_region_name)
