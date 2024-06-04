from osbot_aws.aws.ec2.EC2                          import EC2
from osbot_utils.base_classes.Type_Safe             import Type_Safe
from osbot_utils.decorators.methods.cache_on_self   import cache_on_self


class Create_EC2_Instance(Type_Safe):
    image_id          : str
    instance_type     : str
    key_name          : str
    target_region     : str
    security_group_id : str
    spot_instance     : bool = True
    tags              : dict

    @cache_on_self
    def ec2(self):
        return EC2()

    def create_kwargs(self):
        return  dict(image_id          = self.image_id           ,
                     instance_type     = self.instance_type      ,
                     key_name          = self.key_name           ,
                     target_region     = self.target_region      ,
                     security_group_id = self.security_group_id  ,
                     spot_instance     = self.spot_instance      ,
                     tags              = self.tags               )

    def set_image_id__aws_linux__for_region(self, region):
        return self.ec2().amis()
