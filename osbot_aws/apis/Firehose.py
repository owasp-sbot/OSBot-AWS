import json

from osbot_aws.aws.iam.IAM import IAM
from osbot_utils.decorators.methods.cache import cache
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.decorators.methods.catch import catch

from osbot_aws.aws.lambda_.Lambda import Lambda

from osbot_aws.apis.Session import Session


class Firehose:

    @cache_on_self
    def firehose(self):
        return Session().client('firehose')

    def _convert_to_bytes(self,data=''):
        if type(data) is not bytes:
            if type(data) is not str:
                data = json.dumps(data)
            data += '\n'                    # need to do this or we will get a massive list of entries
        return data.encode()

    @catch
    def add_processing_lambda(self, stream_name, lambda_name):
        function_arn = Lambda(lambda_name).function_arn()
        update_data =  { 'ProcessingConfiguration': {
                            'Enabled'   : True,
                            'Processors': [{ 'Type': 'Lambda',
                                              'Parameters': [{
                                                  'ParameterName' : 'LambdaArn',
                                                  'PameterValue': function_arn}]}]}}
        return self.destination_update(stream_name, update_data)

    def add_processing_lambda_set_lambda_permission(self, lambda_arn):
        statement_id = 'allow_firehose_to_invoke_lambda_function'
        action       = 'lambda:InvokeFunction'
        principal    = 'firehose.amazonaws.com'
        aws_lambda   = Lambda()
        aws_lambda.permission_delete(lambda_arn, statement_id)
        return aws_lambda.permission_add(lambda_arn, statement_id, action, principal, )

    def add_record(self, stream_name, record):
        params = {'DeliveryStreamName': stream_name ,
                  'Record': {'Data': self._convert_to_bytes(record) }}
        return self.firehose().put_record(**params)

    def add_records(self, stream_name, records):
        items = []
        for record in records:
            items.append({'Data': self._convert_to_bytes(record)})
        params = {'DeliveryStreamName': stream_name , 'Records': items}
        return self.firehose().put_record_batch(**params)

    @catch
    def destination_update(self, stream_name, update_data, destination_index=0):
        stream_info = self.stream(stream_name)
        version_id  = stream_info.get('VersionId')
        destination_id = stream_info.get('Destinations')[destination_index].get('DestinationId')

        params = { 'DeliveryStreamName'             : stream_name,
                   'CurrentDeliveryStreamVersionId' : version_id,
                   'DestinationId'                  : destination_id,
                   'ExtendedS3DestinationUpdate'    : update_data
                   }
        return self.firehose().update_destination(**params)



    @catch
    def stream(self, stream_name):
        return self.firehose().describe_delivery_stream(DeliveryStreamName=stream_name).get('DeliveryStreamDescription')

    @catch
    def stream_create(self, stream_name, s3_bucket, s3_prefix, compression='UNCOMPRESSED'):
        account_id = IAM().account_id()
        role       = 'firehose_delivery_role'
        params     = { "DeliveryStreamName": stream_name,
                       "DeliveryStreamType": "DirectPut",
                       'ExtendedS3DestinationConfiguration': {
                            "RoleARN"          : f"arn:aws:iam::{account_id}:role/{role}",
                            "BucketARN"        : f"arn:aws:s3:::{s3_bucket}",
                            "Prefix"           : f"{s3_prefix}/",
                            "CompressionFormat": compression   }}
        return self.firehose().create_delivery_stream(**params)

    @catch
    def stream_delete(self, stream_name):
        return self.firehose().delete_delivery_stream(DeliveryStreamName=stream_name)

    def streams(self):
        return self.firehose().list_delivery_streams().get('DeliveryStreamNames')


