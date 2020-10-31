from osbot_aws.apis.Lambda import Lambda

from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.Firehose import Firehose


class test_Firehose(Test_Helper):

    def setUp(self):
        super().setUp()
        self.firehose = Firehose()
        self.stream_name = 'test-delivery-stream'

    def test_firehose(self):
        assert type(self.firehose.firehose()).__name__ == 'Firehose'

    def test_add_processing_lambda(self):
        self.result = self.firehose.add_processing_lambda(stream_name=self.stream_name, lambda_name='gw_bot.lambdas.gw.proxy.on_firehose_record')

    def test_add_processing_lambda_set_lambda_permission(self):
        lambda_arn = Lambda('gw_bot.lambdas.gw.proxy.on_firehose_record').function_Arn()
        self.result = self.firehose.add_processing_lambda_set_lambda_permission(lambda_arn=lambda_arn)

    def test_add_record(self):
        data = {'now as an' :'json object with actually encoding (2)\n\n after enter'}
        self.result = self.firehose.add_record(self.stream_name, data)

    def test_add_records(self):
        data = {'now as an': 'json object with actually encoding (2)\n\n after enter'}
        array = [{'aaaa': 'record', 'bbbb': 'records'}]

        self.firehose.add_record (self.stream_name, data)
        self.firehose.add_records(self.stream_name, array)
        self.firehose.add_records(self.stream_name, array)
        self.firehose.add_record (self.stream_name, data)
        self.firehose.add_records(self.stream_name, array)

    def test_destination_update(self):
        update_item = {'IntervalInSeconds': 60, 'SizeInMBs': 2}
        update_data = { 'BufferingHints' : update_item }
        assert self.firehose.destination_update(self.stream_name, update_data).get('error') is None
        assert self.firehose.stream(self.stream_name).get('Destinations').pop().get('ExtendedS3DestinationDescription').get('BufferingHints') == update_item

    def test_stream(self):
        #stream_name = self.firehose.streams().pop()
        self.result = self.firehose.stream(self.stream_name)

    def test_stream_create_delete(self):
        stream_name = 'new_test_stream'
        s3_bucket   = 'gw-tf-cloud-trails'
        s3_prefix   = 'test-firehose-data-2'
        self.firehose.stream_create(stream_name, s3_bucket, s3_prefix)
        #todo: add detection if the stream has been created, since the next lines (stream and stream_delete) doesn't work until the stream is active
        assert self.firehose.stream(stream_name).get('DeliveryStreamName') == stream_name
        self.result = self.firehose.stream_delete(stream_name)
        # same here need to wait until the status of the stream has moved from 'Deleting'
        assert self.firehose.stream(stream_name).get('error') is not None

    def test_streams(self):
        assert len(self.firehose.streams()) > 0