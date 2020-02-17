from gw_bot.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.Firehose import Firehose
from osbot_aws.apis.Kinesis import Kinesis


class test_Kinesis(Test_Helper):

    def setUp(self):
        super().setUp()
        self.kinesis = Kinesis()

    def test_kinesis(self):
        assert type(self.kinesis.kinesis()).__name__ == 'Kinesis'

    def test_streams(self):
        self.result = self.kinesis.streams()