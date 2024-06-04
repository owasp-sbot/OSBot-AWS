from os import chmod

from osbot_aws.aws.ec2.AMI import AMI
from osbot_aws.aws.ec2.EC2                          import EC2
from osbot_utils.base_classes.Type_Safe             import Type_Safe
from osbot_utils.decorators.methods.cache_on_self   import cache_on_self
from osbot_utils.utils.Files import current_temp_folder, folder_create, parent_folder, file_exists, file_create, \
    file_not_exists

DEFAULT__EC2__SECURITY_GROUP_NAME__WITH_SSH = 'security_group_with_only_ssh'
DEFAULT__EC2__KEY_NAME_FORMAT               = '{account_id}__osbot__{region_name}'
DEFAULT__EC2__KEY_FILE__LOCATION            = '{current_temp_folder}/osbot_aws_keys/{key_name}.pem'


# todo:
# need to make sure that the current identity has ec2:* and these extra iam permissions
# {
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Sid": "VisualEditor0",
#             "Effect": "Allow",
#             "Action": [
#                 "iam:CreateServiceLinkedRole",
#                 "iam:PutRolePolicy"
#             ],
#             "Resource": "*"
#         }
#     ]
# }
# this should be in a generic policy called something like Policy__EC__required_to_create_instances
class EC2__Create__Instance(Type_Safe):
    image_id          : str
    instance_type     : str
    key_name          : str
    security_group_id : str
    spot_instance     : bool = True
    tags              : dict
    ec2               : EC2

    def create_kwargs(self):
        return  dict(image_id          = self.image_id           ,
                     instance_type     = self.instance_type      ,
                     key_name          = self.key_name           ,
                     security_group_id = self.security_group_id  ,
                     spot_instance     = self.spot_instance      ,
                     tags              = self.tags               )

    def ami_amazon_linux_3_x86_64(self):
        return AMI().amazon_linux_3_x86_64()


    def create_instance(self):
        create_kwargs = self.create_kwargs()
        return self.ec2.instance_create(**create_kwargs)

    def create_instance__with_amazon_linux__t3_nano__ssh_sg__spot(self):
        self.setup__with_amazon_linux__t3_nano__ssh_sg__spot()
        return self.create_instance()

    def setup__with_amazon_linux__t3_nano__ssh_sg__spot(self):
        self.image_id          = self.ami_amazon_linux_3_x86_64()
        self.instance_type     = 't3.nano'
        self.key_name          = self.key_name__create_if_doesnt_exist()
        self.security_group_id = self.security_group_with_ssh()
        self.spot_instance     = True
        self.tags              = {'created-by': 'OSBot_AWS.Create_EC2_Instance'}


    def key_name__create_if_doesnt_exist(self):
        key_name = self.key_name__from_account_id_and_region_name()
        key_path = self.path_key_file()
        key_details = self.ec2.key_pair(key_pair_name=key_name)
        if key_details:
            if file_not_exists(key_path):   # f"Key pair {key_name} exists in EC2 but the local key file not found: {key_path}")
                self.ec2.key_pair_delete(key_pair_name=key_name)
            else:
                return key_name

        key_data     = self.ec2.key_pair_create(key_name=key_name)
        key_contents = key_data.get('KeyMaterial')
        file_create(key_path, key_contents)             # create file
        chmod(path=key_path, mode= 0o400)               # set the correct permissions
        return key_name

    def key_name__from_account_id_and_region_name(self):
        key_name = DEFAULT__EC2__KEY_NAME_FORMAT.format(account_id=self.ec2.aws_config.account_id(), region_name=self.ec2.aws_config.region_name())
        return key_name

    def path_key_file(self):
        key_name = self.key_name__from_account_id_and_region_name()
        key_file = DEFAULT__EC2__KEY_FILE__LOCATION.format(current_temp_folder=current_temp_folder(), key_name=key_name)
        folder_create(parent_folder(key_file))
        return key_file

    def security_group_with_ssh(self):
        security_group = self.ec2.security_group(security_group_name=DEFAULT__EC2__SECURITY_GROUP_NAME__WITH_SSH)
        if security_group is None:
            # create security group
            security_group_name = DEFAULT__EC2__SECURITY_GROUP_NAME__WITH_SSH
            description         = DEFAULT__EC2__SECURITY_GROUP_NAME__WITH_SSH
            result              = self.ec2.security_group_create(security_group_name=security_group_name, description=description)
            security_group_id   = result.get('data').get('security_group_id')
            # enable SSH
            self.ec2.security_group_authorize_ingress(security_group_id, port=22)
            return security_group_id

        security_group_id = security_group.get('GroupId')
        return security_group_id





