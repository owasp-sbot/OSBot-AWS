# todo: refactor to osbot_dock since that is where the API_Docker and Docker_Image exist
from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.apis.ECR import ECR

from osbot_utils.utils.Files import path_combine

class Create_Image_ECR:

    def __init__(self, image_name, path_images=None, image_tag='latest') -> object:
        from osbot_docker.apis.API_Docker import API_Docker
        from osbot_docker.apis.Docker_Image import Docker_Image
        self.api_docker      = API_Docker()
        self.ecr             = ECR()
        self.aws_config      = AWS_Config()
        self.image_name      = image_name
        self.image_tag       = image_tag
        self.path_images     = path_images or path_combine(__file__, '../../images')
        self.docker_image    = Docker_Image(image_name=self.image_repository(),image_tag=self.image_tag, api_docker=self.api_docker)

    def build_image(self):
        result       = self.docker_image.build(self.path_image())
        return result

    def create_repository(self):
        self.ecr.repository_create(self.image_name)
        return self.repository_exists()

    def delete_repository(self):
        return self.ecr.repository_delete(self.image_name)

    def full_image_name(self):
        return f'{self.image_repository()}:{self.image_tag}'

    def image_repository(self):
        account_id = self.aws_config.aws_session_account_id()
        region     = self.aws_config.aws_session_region_name()
        return f'{account_id}.dkr.ecr.{region}.amazonaws.com/{self.image_name}'

    def ecr_login(self):
        auth_data = self.ecr.authorization_token()
        return self.api_docker.registry_login(registry=auth_data.get('registry'),
                                              username=auth_data.get('username'),
                                              password=auth_data.get('password'))


    def path_image(self):
        return path_combine(self.path_images, self.image_name)

    def push_image(self):
        auth_result = self.ecr_login()                             # make sure we are logged in
        push_json_lines = self.docker_image.image_push()
        return dict(auth_result=auth_result, push_json_lines=push_json_lines)

    def run_locally(self):
        full_image_name = self.full_image_name()
        return self.api_docker.docker_run(full_image_name)

    def create(self):
        create_repository = self.create_repository   ()
        ecr_login         = self.ecr_login           ()
        build_image       = self.build_image         ()
        push_image        = self.push_image          ()
        return {'create_repository' : create_repository,
                'ecr_login'         : ecr_login        ,
                'build_image'       : build_image      ,
                'push_image'        : push_image       }

    def repository_exists(self):
        return self.ecr.repository_exists(self.image_name)
