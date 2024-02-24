import re
from functools import cache
from unittest import TestCase

from botocore.exceptions import ClientError
from dotenv import load_dotenv

from osbot_aws.aws.bedrock.Bedrock import Bedrock
from osbot_aws.aws.bedrock.models.anthropic.Anthropic__Claude_Instant_V1 import Anthropic__Claude_Instant_V1
from osbot_aws.aws.boto3.Capture_Boto3_Error import capture_boto3_error
from osbot_aws.aws.iam.Capture_IAM_Exception import capture_iam_exception, Capture_IAM_Exception
from osbot_aws.aws.iam.IAM_Assume_Role import IAM_Assume_Role
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.testing.Patch_Print import Patch_Print
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Lists import list_contains_list
from osbot_utils.utils.Misc import list_set
from osbot_utils.utils.Objects import type_full_name, obj_info

class Bedrock__with_temp_role(Bedrock):

    def iam_assume_role(self, service):
        load_dotenv()
        #service         = "bedrock"
        action          = "*"
        resource        = "*"
        role_name       = 'osbot__temp_role_for__test_Bedrock'
        policies_to_add = [dict(service=service, action=action, resource=resource)]
        iam_assume_role = IAM_Assume_Role(role_name=role_name, policies_to_add=policies_to_add)
        iam_assume_role.create_role(recreate=False)
        #iam_assume_role.credentials_reset()
        return iam_assume_role

    @cache_on_self
    def client(self):
        service = "bedrock"
        return self.iam_assume_role(service).boto3_client(service_name=service, region_name=self.region_name)

    @cache_on_self
    def runtime(self):
        service = "bedrock-runtime"
        return self.iam_assume_role(service).boto3_client(service_name=service, region_name=self.region_name)

class test_Bedrock(TestCase):

    def setUp(self):
        self.region_name = 'us-east-1'
        self.bedrock     = Bedrock__with_temp_role(region_name=self.region_name)

    def test___init__(self):
        assert type_full_name(self.bedrock        ) == 'test_Bedrock.Bedrock__with_temp_role'

    def test_client(self):
        client = self.bedrock.client()
        assert type_full_name(client)                      == 'botocore.client.Bedrock'
        assert client.meta.region_name                     == 'us-east-1'
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

    def test_runtime(self):
        runtime = self.bedrock.runtime()
        assert type_full_name(runtime)                      == 'botocore.client.BedrockRuntime'
        assert runtime.meta.region_name                     == 'us-east-1'
        assert list_set(runtime.meta.method_to_api_mapping) == ['invoke_model', 'invoke_model_with_response_stream']

    @capture_boto3_error
    def test_model_invoke(self):
        prompt    = "What is the capital of France?"
        response  = ' The capital of France is Paris.'
        model     = Anthropic__Claude_Instant_V1(prompt=prompt)
        model_id  = model.model_id
        body      = model.body()
        result    = self.bedrock.model_invoke(model_id, body)
        assert result == { 'completion'   : response                          ,
                           'stop'         : '\n\nHuman:'                      ,
                           'stop_reason'  : 'stop_sequence'                   }

        # model_id    = 'cohere.command-light-text-v14'
        # model_id    = 'meta.llama2-13b-chat-v1'

    #@capture_iam_exception
    def test_models(self):
        expected_attributes = ['customizationsSupported', 'inferenceTypesSupported', 'inputModalities', 'modelArn',
                               'modelId', 'modelLifecycle', 'modelName', 'outputModalities',
                               'providerName', ] #'responseStreamingSupported'
        models = self.bedrock.models()
        for model  in models:
            assert list_contains_list(list_set(model), expected_attributes)
            assert list_set(model.get('modelLifecycle')) == ['status']
        assert len(models) == 45

    def test_models_active(self):
        models                     = self.bedrock.models_active()
        models_a1_labs             = models.get('AI21 Labs'   )
        models_a1_labs__text       = models.get('AI21 Labs'   ).get('TEXT')
        models_amazon              = models.get('Amazon'      )
        models_amazon__embedding   = models.get('Amazon'      ).get('EMBEDDING')
        models_amazon__image       = models.get('Amazon'      ).get('IMAGE'    )
        models_amazon__text        = models.get('Amazon'      ).get('TEXT')
        models_anthropic           = models.get('Anthropic'   )
        models_anthropic__text     = models.get('Anthropic'   ).get('TEXT')
        models_cohere              = models.get('Cohere'      )
        models_cohere___text       = models.get('Cohere'      ).get('TEXT')
        models_cohere___embedding  = models.get('Cohere'      ).get('EMBEDDING')
        models_meta                = models.get('Meta'        )
        models_meta__text          = models.get('Meta'        ).get('TEXT')
        models_stability_ai        = models.get('Stability AI')
        models_stability_ai__image = models.get('Stability AI').get("IMAGE")


        assert list_set(models                    ) == ['AI21 Labs', 'Amazon', 'Anthropic', 'Cohere', 'Meta', 'Stability AI']
        assert list_set(models_a1_labs            ) == ['TEXT'                         ]
        assert list_set(models_amazon             ) == ['EMBEDDING', 'IMAGE', 'TEXT'   ]
        assert list_set(models_anthropic          ) == ['TEXT'                         ]
        assert list_set(models_cohere             ) == ['EMBEDDING', 'TEXT'            ]
        assert list_set(models_meta               ) == ['TEXT'                         ]
        assert list_set(models_stability_ai       ) == ['IMAGE'                        ]
        assert list_set(models_a1_labs__text      ) == ['ai21.j2-grande-instruct'         , 'ai21.j2-jumbo-instruct'            , 'ai21.j2-mid'                  , 'ai21.j2-mid-v1'                , 'ai21.j2-ultra'                  , 'ai21.j2-ultra-v1'                                                                       ]
        assert list_set(models_amazon__embedding  ) == ['amazon.titan-embed-g1-text-02'   , 'amazon.titan-embed-image-v1'       , 'amazon.titan-embed-image-v1:0', 'amazon.titan-embed-text-v1'    , 'amazon.titan-embed-text-v1:2:8k'                                                                                           ]
        assert list_set(models_amazon__image      ) == ['amazon.titan-image-generator-v1' , 'amazon.titan-image-generator-v1:0'                                                                                                                                                                                                  ]
        assert list_set(models_amazon__text       ) == ['amazon.titan-text-express-v1'    , 'amazon.titan-text-express-v1:0:8k' , 'amazon.titan-text-lite-v1'    , 'amazon.titan-text-lite-v1:0:4k', 'amazon.titan-tg1-large'                                                                                                    ]
        assert list_set(models_anthropic__text    ) == ['anthropic.claude-instant-v1'     , 'anthropic.claude-instant-v1:2:100k', 'anthropic.claude-v2'          , 'anthropic.claude-v2:0:100k'    , 'anthropic.claude-v2:0:18k'      , 'anthropic.claude-v2:1'       , 'anthropic.claude-v2:1:18k', 'anthropic.claude-v2:1:200k']
        assert list_set(models_cohere___text      ) == ['cohere.command-light-text-v14'   , 'cohere.command-light-text-v14:7:4k', 'cohere.command-text-v14'      , 'cohere.command-text-v14:7:4k'                                                                                                                                ]
        assert list_set(models_cohere___embedding ) == ['cohere.embed-english-v3'         , 'cohere.embed-multilingual-v3'                                                                                                                                                                                                       ]
        assert list_set(models_meta__text         ) == ['meta.llama2-13b-chat-v1'         , 'meta.llama2-13b-chat-v1:0:4k'      , 'meta.llama2-13b-v1'           , 'meta.llama2-13b-v1:0:4k'       , 'meta.llama2-70b-chat-v1'        , 'meta.llama2-70b-chat-v1:0:4k', 'meta.llama2-70b-v1'       , 'meta.llama2-70b-v1:0:4k'   ]
        assert list_set(models_stability_ai__image) == ['stability.stable-diffusion-xl-v1', 'stability.stable-diffusion-xl-v1:0'                                                                                                                                                                                                 ]


