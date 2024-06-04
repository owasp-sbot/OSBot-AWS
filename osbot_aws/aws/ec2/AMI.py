from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.aws.ec2.EC2 import EC2
from osbot_aws.aws.sts.STS import STS
from osbot_utils.base_classes.Type_Safe import Type_Safe
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.helpers.Local_Cache import Local_Cache

AWS__AMIS__MAPPINGS = {'eu-west-1' : {'x86_64': { 'amazon-linux-3': 'ami-04fe22dfadec6f0b6' },
                                      'arm64' : { 'amazon-linux-3': 'ami-05172b510cbeb4f59' }},
                       'eu-west-2' : {'x86_64': { 'amazon-linux-3': 'ami-06373f703eb245f45' },
                                      'arm64' : { 'amazon-linux-3': 'ami-06c0324315b2eb40d' }}}



class AMI(Type_Safe):
    aws_config: AWS_Config
    ec2       : EC2
    # def __init__(self):
    #     self.current_region_name = self.sts().current_region_name()

    # @cache_on_self
    # def sts(self):
    #     return STS()
    #
    def all_amis__local_cache(self):
        return Local_Cache('all_amazon_amis')

    def all_amis__from_amazon__cached(self):                    # this is a 15Mb file!
        local_cache = self.all_amis__local_cache()
        if local_cache.cache_exists():
            return local_cache.data().get('amazon_amis')
        else:
            all_amazon_amis = self.ec2.amis(owner='amazon')
            amis_data = {'amazon_amis': all_amazon_amis}
            local_cache.add_data(amis_data)
            return all_amazon_amis

    @cache_on_self
    def ami_mappings_per_region(self):                                                          # todo find way to pre-create these in a performant way (for all regions)
        return AWS__AMIS__MAPPINGS

    def get_ami_for_image(self, image_name, region_name, architecture):
        return self.ami_mappings_per_region().get(region_name, {}).get(architecture, {}).get(image_name,'')

    def amazon_linux_3(self, architecture='x86_64'):
        image_name = 'amazon-linux-3'
        return self.get_ami_for_image(image_name=image_name, region_name=self.aws_config.region_name(), architecture=architecture)

    def amazon_linux_3_x86_64(self):
        return self.amazon_linux_3(architecture='x86_64')

    def amazon_linux_3_arm64(self):
        return self.amazon_linux_3(architecture='arm64')