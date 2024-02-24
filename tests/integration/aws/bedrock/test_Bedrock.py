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

    @capture_iam_exception
    def test_models(self):
        self.bedrock.models()