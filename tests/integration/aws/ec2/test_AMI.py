from unittest import TestCase

import pytest
from osbot_aws.aws.ec2.AMI                      import AMI
from osbot_aws.aws.ec2.utils.TestCase__EC2      import TestCase__EC2
from osbot_aws.testing.TestCase__Boto3_Cache    import TestCase__Boto3_Cache
from osbot_utils.utils.Lists                    import list_index_by


class test_AMI(TestCase__Boto3_Cache, TestCase__EC2):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        TestCase__EC2.setUpClass()

    def setUp(self) -> None:
        self.ami                 = AMI(ec2=self.ec2)

    @pytest.mark.skip("figure out better way to do (or cache) this , since this is a 15M download")
    def test_all_amis__from_amazon__cached(self):
        with self.ami as _:
            amazon_amis = _.all_amis__from_amazon__cached()
            amazon_amis_by_id = list_index_by(amazon_amis, 'ImageId')
            assert len(amazon_amis) > 13.5 * 1000

            # todo: figure out to get a good list of AMIs, namely the amazon Linux 3. I can't ssem to be able to get a good query that returns the AMI ids that we get in AWS console
            # #pprint(amazon_amis_by_id.get('ami-074882b79a16e2e6e'))
            #
            # #pprint(_.ec2.ami('ami-00f8b1192da5566c5'))
            # #pprint(_.ec2.amis(owner='amazon', name='amzn2-ami-hvm-2.0*'))
            # #matches = _.ec2.amis(owner='amazon', name='al2023-ami-ecs-hvm-2023*')#, architecture='x86_64')
            # #matches = _.ec2.amis(owner='amazon', description='Amazon?Linux?AMI?2023?0*')
            # matches = _.ec2.amis(owner='amazon', description='Amazon Linux 2023 AMI 2023.4.20240528.0 x86_64 HVM kernel-6.10')
            # pprint(f'there where {len(matches)}')
            #
            # pprint(matches)

    @pytest.mark.skip("figure out better way to do (or cache) this , since this is a 15M download")
    def test_all_amis__local_cache(self):
        with self.ami as _:
            local_cache = _.all_amis__local_cache()
            assert local_cache.cache_file_size()             > 15 * 1000 * 1000 # the file has more than 15Mb
            assert len(local_cache.data().get('amazon_amis')) > 13.5 * 1000     # and more than 13.5k entries


    def test_ami_mappings_per_region(self):
        with self.ami as _:
            amis = _.ami_mappings_per_region()
            current_region = _.aws_config.region_name()
            architecture_data  = amis.get(current_region)
            for architecture, image_data in architecture_data.items():
                for image_name, image_id in image_data.items():
                    ami_details = _.ec2.ami(image_id)
                    assert ami_details.get('Architecture') == architecture
                    assert ami_details.get('Name').startswith('al2023-ami-2023.4.')


    def test_amazon_linux_3_x86_64(self):
        current_region = self.ami.aws_config.region_name()
        architecture   = 'x86_64'
        image_name     = 'amazon-linux-3'
        ami_id         = self.ami.get_ami_for_image(image_name, current_region, architecture)
        assert self.ami.amazon_linux_3_x86_64() == ami_id
