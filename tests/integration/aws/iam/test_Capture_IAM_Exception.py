from unittest import TestCase

from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.aws.bedrock.Bedrock import Bedrock
from osbot_aws.aws.dynamo_db.Dynamo_DB import Dynamo_DB
from osbot_aws.aws.iam.Capture_IAM_Exception import Capture_IAM_Exception
from osbot_aws.testing.Pytest import skip_pytest___aws_pytest_user_name__is_not_set
from tests.integration.aws.iam.test_IAM import IAM_USER_NAME__OSBOT_AWS


class test_Capture_IAM_Exception(TestCase):

    @classmethod
    def setUpClass(cls):
        skip_pytest___aws_pytest_user_name__is_not_set()

    def setUp(self):
        self.aws_config = AWS_Config()
        self.account_id = self.aws_config.account_id()

    def test__enter__exit(self):
        with Capture_IAM_Exception() as _:
            Dynamo_DB().tables()
        assert _.permission_required == { 'account_id'  : self.account_id           ,
                                          'action'      : 'ListTables'              ,
                                          'event'       : 'IAM exception triggered' ,
                                          'service'     : 'dynamodb'                ,
                                          'status'      : 'ok'                      ,
                                          'user'        : IAM_USER_NAME__OSBOT_AWS  }
        with Capture_IAM_Exception() as _:
            pass
        assert _.permission_required == {'event': 'no IAM exception triggered', 'status': 'error'}