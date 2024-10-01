import boto3

from osbot_aws.aws.dynamo_db.Dynamo_DB import Dynamo_DB
from osbot_utils.testing.Temp_Env_Vars  import Temp_Env_Vars
from unittest                           import TestCase
from osbot_utils.testing.Hook_Method    import Hook_Method
from osbot_utils.utils.Env              import get_env

TEST__AWS_ACCOUNT_ID        = '000011110000'
TEST__AWS_DEFAULT_REGION    = 'eu-west-1'
TEST__AWS_ACCESS_KEY_ID     = 'aaaaaaaaa'
TEST__AWS_SECRET_ACCESS_KEY = 'bbbbbbbbb'
URL_DOCKER__DYNAMODB__LOCAL = 'http://localhost:8000'

class TestCase__Dynamo_DB__Local(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.aws_account_id          = get_env('AWS_ACCOUNT_ID'       , TEST__AWS_ACCOUNT_ID       )         # use existing values if they already exist
        cls.aws_default_region      = get_env('AWS_DEFAULT_REGION'   , TEST__AWS_DEFAULT_REGION   )
        cls.aws_access_key_id       = get_env('AWS_ACCESS_KEY_ID'    , TEST__AWS_ACCESS_KEY_ID    )         # this is neeed by create table
        cls.aws_secret_access_key   = get_env('AWS_SECRET_ACCESS_KEY', TEST__AWS_SECRET_ACCESS_KEY)
        tmp_vars_values             = dict(AWS_ACCOUNT_ID        = cls.aws_account_id       ,           # todo: find better way to do this, since this will impact all code executed in the current test
                                           AWS_DEFAULT_REGION    = cls.aws_default_region   ,
                                           AWS_ACCESS_KEY_ID     = cls.aws_account_id       ,
                                           AWS_SECRET_ACCESS_KEY = cls.aws_secret_access_key)
        cls.tmp_env_vars            = Temp_Env_Vars(env_vars=tmp_vars_values).set_vars()
        cls.hook_method             = Hook_Method(Dynamo_DB, 'client'     )              # todo: see if we also need to hook the main S3 class (from osbot_aws)
        cls.hook_method.mock_call   = cls.dynamo_db__client
        cls.hook_method.wrap()
        cls.dynamo_db               = Dynamo_DB()

    @classmethod
    def tearDownClass(cls):
        cls.hook_method.unwrap()
        cls.tmp_env_vars.restore_vars()

    def dynamo_db__client(self):
        return boto3.client('dynamodb', endpoint_url=URL_DOCKER__DYNAMODB__LOCAL)