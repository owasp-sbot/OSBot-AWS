from unittest import TestCase
from osbot_utils.utils.Misc import random_string
from osbot_aws.AWS_Config import AWS_Config
from osbot_utils.utils.Dev import Dev, pprint
from osbot_aws.apis.ECR import ECR


#STS().check_current_session_credentials()

class test_ECR(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.aws_config = AWS_Config()
        cls.account_id = cls.aws_config.aws_session_account_id()
        cls.ecr        = ECR()
        cls.name       = 'an_test_repository'
        cls.tags       = {'an_tag':'an_value'}

        assert cls.ecr.repository_exists(cls.name) is False
        cls.result_create = cls.ecr.repository_create(name=cls.name, tags=cls.tags)
        assert cls.ecr.repository_exists(cls.name) is True

    @classmethod
    def tearDownClass(cls) -> None:
        assert cls.ecr.repository_exists(cls.name) is True
        assert cls.ecr.repository_delete(cls.name) is True
        assert cls.ecr.repository_exists(cls.name) is False

    #def test_images(self):
    #    images = self.ecr.images()
    #    pprint(images)

    def test_repository_create(self):
        pprint(self.result_create)

        assert self.ecr.repository_create(name=self.name) == { 'message': f'repository {self.name} already existed','status': 'warning'}

    def test_repository_delete(self):
        assert self.ecr.repository_delete(random_string()) is False

    def test_repository_info(self):
        assert self.ecr.repository_info(self.name).get('repositoryName') == self.name
        assert self.ecr.repository_info(random_string()) is None

    def test_repositories(self):
        result = self.ecr.repositories(index_by='repositoryName')
        assert self.name in result

    def test_registry(self):
        result = self.ecr.registry()
        assert result == {'registry_id': self.account_id, 'replication_configuration': {'rules': []}}



