from osbot_utils.base_classes.Type_Safe import Type_Safe



class Create_AMI__OSBot_AWS(Type_Safe):

    def create_kwargs(self, image_id=None):
        pass
        # instance_type        = 't3.nano'
        # spot_instance        = True
        # security_group_id    = environ.get('EC2_TESTS__SECURITY_GROUP_ID')
        # ssh_key_name         = environ.get('EC2_TESTS__PATH_SSH_KEY_FILE_NAME')
        # iam_instance_profile = {'Name': self.iam_role_name                    }
        #
        # return  dict(image_id             = image_id or 'ami-0136026a91d5f4151' ,
        #              iam_instance_profile = iam_instance_profile                ,
        #              key_name             = ssh_key_name                        ,
        #              security_group_id    = security_group_id                   ,
        #              instance_type        = instance_type                       ,
        #              spot_instance        = spot_instance                       )

    def create_ec2_instance(self):
        pass
        # ec2_instance = EC2_Instance()
        # ec2_instance.create_kwargs = self.create_kwargs(image_id=image_id)
        # pprint(ec2_instance.create_kwargs)
        # # region_name  = self.aws_config.region_name()
        # # image_id     = AMIS_PER_REGION.get(region_name)
        # return ec2_instance.create()


