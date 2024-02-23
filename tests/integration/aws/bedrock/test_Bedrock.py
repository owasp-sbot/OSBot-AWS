import re
from unittest import TestCase

from botocore.exceptions import ClientError

from osbot_aws.aws.bedrock.Bedrock import Bedrock
from osbot_aws.aws.iam.Capture_IAM_Exception import capture_iam_exception, Capture_IAM_Exception
from osbot_utils.testing.Patch_Print import Patch_Print
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set
from osbot_utils.utils.Objects import type_full_name, obj_info


class test_Bedrock(TestCase):

    def setUp(self):
        self.region_name = 'eu-central-1'
        self.bedrock     = Bedrock(region_name=self.region_name)

    def test___init__(self):
        assert type_full_name(self.bedrock        ) == 'osbot_aws.aws.bedrock.Bedrock.Bedrock'

    def test_client(self):
        client = self.bedrock.client()
        assert type_full_name(client) == 'botocore.client.Bedrock'
        assert client.meta.region_name  == 'eu-central-1'
        assert list_set(client.meta.method_to_api_mapping) == [ 'create_model_customization_job'                ,
                                                                'create_provisioned_model_throughput'           ,
                                                                'delete_custom_model'                           ,
                                                                'delete_model_invocation_logging_configuration' ,
                                                                'delete_provisioned_model_throughput'           ,
                                                                'get_custom_model'                              ,
                                                                'get_foundation_model'                          ,
                                                                'get_model_customization_job'                   ,
                                                                'get_model_invocation_logging_configuration'    ,
                                                                'get_provisioned_model_throughput'              ,
                                                                'list_custom_models'                            ,
                                                                'list_foundation_models'                        ,
                                                                'list_model_customization_jobs'                 ,
                                                                'list_provisioned_model_throughputs'            ,
                                                                'list_tags_for_resource'                        ,
                                                                'put_model_invocation_logging_configuration'    ,
                                                                'stop_model_customization_job'                  ,
                                                                'tag_resource'                                  ,
                                                                'untag_resource'                                ,
                                                                'update_provisioned_model_throughput'           ]

    #@capture_iam_exception
    def test_models(self):
        with Capture_IAM_Exception() as _:
            self.bedrock.models()
        assert _.permission_required == { 'account_id'  : '470426667096',
                                          'action'      : 'ListFoundationModels',
                                          'event'       : 'exception triggered',
                                          'service'     : 'bedrock',
                                          'status'      : 'ok',
                                          'user'        : 'OSBot-AWS-Dev__Only-IAM'}
        with Capture_IAM_Exception() as _:
            pass
        assert _.permission_required == {'event': 'no exception triggered', 'status': 'error'}


    # def test_models_2(self):
    #
    #     try:
    #         self.bedrock.models()
    #
    #     except ClientError as e:
    #         error_code = e.response['Error']['Code']
    #         if error_code == 'AccessDeniedException':
    #             error_message = e.response['Error']['Message']
    #             print("Access Denied Exception caught.")
    #
    #             # Extracting details from the error message
    #             user_arn_match = re.search(r"User: arn:aws:iam::(\d+):user/([^ ]+) is not authorized", error_message)
    #             required_permission_match = re.search(r"because no identity-based policy allows the ([^:]+):([^ ]+) action", error_message)
    #
    #             if user_arn_match and required_permission_match:
    #                 account_id, user = user_arn_match.groups()
    #                 service, action = required_permission_match.groups()
    #
    #                 permission_required = {
    #                     'service': service,
    #                     'action': action,
    #                     'account_id': account_id,
    #                     'user': user
    #                 }
    #             else:
    #                 permission_required = {
    #                     'service': 'Not found',
    #                     'action': 'Not found',
    #                     'account_id': 'Not found',
    #                     'user': 'Not found'
    #                 }
    #             pprint(permission_required)
    #         else:
    #             print(f"An unexpected error occurred: {e}")
    #     except Exception as e:
    #         # Catch other potential errors
    #         print(f"An error occurred: {e}")