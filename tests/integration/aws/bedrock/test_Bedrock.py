import re
from functools import cache
from unittest import TestCase

from botocore.exceptions import ClientError
from dotenv import load_dotenv

from osbot_aws.aws.bedrock.Bedrock import Bedrock
from osbot_aws.aws.iam.Capture_IAM_Exception import capture_iam_exception, Capture_IAM_Exception
from osbot_aws.aws.iam.IAM_Assume_Role import IAM_Assume_Role
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.testing.Patch_Print import Patch_Print
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set
from osbot_utils.utils.Objects import type_full_name, obj_info

class Bedrock__with_temp_role(Bedrock):

    @cache_on_self
    def client(self):
        load_dotenv()
        service         = "bedrock"
        action          = "*"
        resource        = "*"
        role_name       = 'osbot__temp_role_for__test_Bedrock'
        policies_to_add = [dict(service=service, action=action, resource=resource)]
        iam_assume_role = IAM_Assume_Role(role_name=role_name, policies_to_add=policies_to_add)
        iam_assume_role.create_role(recreate=False)
        #iam_assume_role.credentials_reset()
        return iam_assume_role.boto3_client(service_name=service, region_name=self.region_name)

class test_Bedrock(TestCase):

    def setUp(self):
        self.region_name = 'eu-central-1'
        self.bedrock     = Bedrock__with_temp_role(region_name=self.region_name)

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
        self.bedrock.models()