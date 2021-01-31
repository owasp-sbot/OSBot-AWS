from unittest import TestCase
from osbot_utils.utils.Misc import random_string
from osbot_aws.AWS_Config import AWS_Config
from osbot_utils.utils.Dev import Dev, pprint
from osbot_aws.apis.ECR import ECR


#STS().check_current_session_credentials()

class test_ECR(TestCase):

    ecr             = None
    repository_name = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.aws_config      = AWS_Config()
        cls.account_id      = cls.aws_config.aws_session_account_id()
        cls.ecr             = ECR()
        cls.repository_name = 'an_test_repository'
        cls.repository_tags = {'an_tag':'an_value'}

        assert cls.ecr.repository_exists(cls.repository_name) is False
        cls.result_create = cls.ecr.repository_create(name=cls.repository_name, tags=cls.repository_tags)
        assert cls.ecr.repository_exists(cls.repository_name) is True

    @classmethod
    def tearDownClass(cls) -> None:
        assert cls.ecr.repository_exists(cls.repository_name) is True
        assert cls.ecr.repository_delete(cls.repository_name) is True
        assert cls.ecr.repository_exists(cls.repository_name) is False

    def test_authorization_token(self):
        result = self.ecr.authorization_token()
        pprint(result)

    def test_images(self):
       images = self.ecr.images(self.repository_name)
       pprint(images)

    def test_images_ids(self):
       images = self.ecr.images_ids(self.repository_name)
       pprint(images)

    def test_repository_create(self):
        pprint(self.result_create)

        assert self.ecr.repository_create(name=self.repository_name) == { 'message': f'repository {self.repository_name} already existed','status': 'warning'}

    def test_repository_delete(self):
        assert self.ecr.repository_delete(random_string()) is False

    def test_repository_info(self):
        assert self.ecr.repository_info(self.repository_name).get('repositoryName') == self.repository_name
        assert self.ecr.repository_info(random_string()) is None

    def test_repositories(self):
        result = self.ecr.repositories(index_by='repositoryName')
        assert self.repository_name in result

    def test_registry(self):
        result = self.ecr.registry()
        assert result == {'registry_id': self.account_id, 'replication_configuration': {'rules': []}}



