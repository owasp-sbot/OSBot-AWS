from osbot_aws.aws.sts.STS import STS
from osbot_utils.decorators.methods.cache_on_self import cache_on_self


class AMI:

    def __init__(self):
        self.current_region_name = self.sts().current_region_name()

    @cache_on_self
    def sts(self):
        return STS()

    @cache_on_self
    def ami_mappings_per_region(self):                                                          # todo find way to pre-create these in a performant way (for all regions)
        mappings = {'amazon-linux-2': { 'eu-west-1': 'ami-00f8b1192da5566c5' ,
                                        'eu-west-2': 'ami-074882b79a16e2e6e' }}
        return mappings

    def get_ami_for_image(self, image_name, region_name):
        return self.ami_mappings_per_region().get(image_name,{}).get(region_name,'')

    def amazon_linux_2(self):
        image_name = 'amazon-linux-2'
        return self.get_ami_for_image(image_name=image_name, region_name=self.current_region_name)