from unittest import TestCase

from osbot_utils.utils.Misc import wait

from osbot_aws.helpers.Lambda_Package import Lambda_Package

from osbot_aws.helpers.Create_Image_ECR import Create_Image_ECR
from osbot_aws.AWS_Config import AWS_Config

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import folder_exists, path_combine


class test_Create_Image_ECR(TestCase):

    def setUp(self) -> None:
        #self.ecr_repository = 'osbot_unit_tests'
        self.image_name     = 'ubuntu'
        self._ = Create_Image_ECR(self.image_name)

    # def test_repositories(self):
    #     ecr = ECR()
    #     repos = ecr.repositories(index_by="repositoryName")
    #
    #     pprint(repos)

    def test_build_image(self):
        assert self._.build_image() is True

    def test_create_repository(self):
        assert self._.create_repository() is True

    def test_image_repository(self):
        aws_config = AWS_Config()
        account_id = aws_config.aws_session_account_id()
        region     = aws_config.aws_session_region_name()
        assert self._.image_repository() == f'{account_id}.dkr.ecr.{region}.amazonaws.com/{self.image_name}'

    def test_ecr_login(self):
        assert self._.ecr_login() == {'IdentityToken': '', 'Status': 'Login Succeeded'}

    def test_path_image(self):
        assert folder_exists(self._.path_image())

    def test_path_images(self):
        assert folder_exists(self._.path_images)

    def test_push_image(self):
        result = self._.push_image()

        pprint(result)

    def test_create_image__ubuntu(self):
        image_name = 'ubuntu'
        result = Create_Image_ECR(image_name=image_name).create()
        pprint(result)

    def test_create_image__hello_world(self):
        image_name = 'hello-world'
        create_image_ecr = Create_Image_ECR(image_name=image_name)
        #pprint(create_image_ecr.build_image())
        #pprint(create_image_ecr.run_locally())
        pprint(create_image_ecr.create())
