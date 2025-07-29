from osbot_aws.apis.Session                         import URL__LOCAL_STACK__ENDPOINT_URL
from osbot_aws.aws.dynamo_db.Dynamo_DB              import Dynamo_DB
from osbot_aws.testing.TestCase__Dynamo_DB__Local   import TestCase__Dynamo_DB__Local
from osbot_utils.utils.Functions                    import function_name


class test_TestCase__Dynamo_DB__Local(TestCase__Dynamo_DB__Local):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        assert function_name(getattr(Dynamo_DB, 'client')) == 'client'

    # def test__setUpClass(self):
    #     assert self.aws_account_id            == get_env('AWS_ACCOUNT_ID'    , TEST__AWS_ACCOUNT_ID    )
    #     assert self.aws_default_region        == get_env('AWS_DEFAULT_REGION', TEST__AWS_DEFAULT_REGION)
    #
    #     assert self.hook_method.target_module                 == Dynamo_DB
    #     assert self.hook_method.target_method                 == 'client'
    #     assert self.hook_method.wrapper_method                == getattr(Dynamo_DB, 'client')
    #     assert function_name(self.hook_method.target)         == 'client'
    #     assert function_name(self.hook_method.wrapper_method) == 'wrapper_method'
    #     assert function_name(getattr(Dynamo_DB, 'client')   ) == 'wrapper_method'

    def test__check_that_we_are_connected_to_local_stack_version(self):
        dynamo_db = Dynamo_DB()
        assert dynamo_db.client().meta.endpoint_url == URL__LOCAL_STACK__ENDPOINT_URL
        assert dynamo_db.tables() == []