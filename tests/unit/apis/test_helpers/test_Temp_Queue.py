import pytest

from osbot_aws.decorators.aws_inject import aws_inject
from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.test_helpers.Temp_Queue  import Temp_Queue

@pytest.mark.skip('Fix tests')
class test_Temp_Lambda(Test_Helper):

    def setUp(self):
        super().setUp()

    @aws_inject('region,account_id')
    def test_simple_execution(self, region, account_id):
        with Temp_Queue() as _:
            assert _.name_prefix    in  _.queue_name
            assert _.queue.exists() is True
            assert _.queue.queue_url == f'https://{region}.queue.amazonaws.com/{account_id}/{_.queue_name}'