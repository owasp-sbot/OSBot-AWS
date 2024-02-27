from osbot_aws.aws.bedrock.Bedrock__with_temp_role                       import Bedrock__with_temp_role
from osbot_aws.aws.bedrock.models.anthropic.Anthropic__Claude_Instant_V1 import Anthropic__Claude_Instant_V1
from osbot_utils.utils.Lists                                             import list_contains_list
from osbot_utils.utils.Misc                                              import list_set
from osbot_utils.utils.Objects                                           import type_full_name
from osbot_aws.testing.TestCase__Bedrock import TestCase__Bedrock


class test_Bedrock(TestCase__Bedrock):

    def setUp(self):
        self.region_name = 'us-east-1'
        self.bedrock     = Bedrock__with_temp_role(region_name=self.region_name)

    def test___init__(self):
        assert type_full_name(self.bedrock        ) == 'osbot_aws.aws.bedrock.Bedrock__with_temp_role.Bedrock__with_temp_role'

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

    #@capture_boto3_error
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

    def test_models_active__on_demand(self):
        active_models = self.bedrock.models_active()
        assert list_set(active_models) == ['ON_DEMAND', 'PROVISIONED']


        models                     = active_models.get('ON_DEMAND')
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

        bug_in__amazon__embedding = 'amazon.titan-embed-image-v1:0'
        bug_in__anthropic__text   = 'anthropic.claude-v2:1'
        bug_in__amazon__image     = 'amazon.titan-image-generator-v1:0'

        assert list_set(models                    ) == ['AI21 Labs', 'Amazon', 'Anthropic', 'Cohere', 'Meta', 'Stability AI']
        assert list_set(models_a1_labs            ) == ['TEXT'                         ]
        assert list_set(models_amazon             ) == ['EMBEDDING', 'IMAGE', 'TEXT'   ]
        assert list_set(models_anthropic          ) == ['TEXT'                         ]
        assert list_set(models_cohere             ) == ['EMBEDDING', 'TEXT'            ]
        assert list_set(models_meta               ) == ['TEXT'                         ]
        assert list_set(models_stability_ai       ) == ['IMAGE'                        ]

        assert list_set(models_a1_labs__text      ) == ['ai21.j2-grande-instruct'         , 'ai21.j2-jumbo-instruct'      , 'ai21.j2-mid'              , 'ai21.j2-mid-v1'            , 'ai21.j2-ultra', 'ai21.j2-ultra-v1']
        assert list_set(models_amazon__embedding  ) == ['amazon.titan-embed-g1-text-02'   , 'amazon.titan-embed-image-v1' , bug_in__amazon__embedding  , 'amazon.titan-embed-text-v1',                                    ]
        assert list_set(models_amazon__image      ) == ['amazon.titan-image-generator-v1' , bug_in__amazon__image                                                                                                         ]
        assert list_set(models_amazon__text       ) == ['amazon.titan-text-express-v1'    , 'amazon.titan-text-lite-v1'   ,  'amazon.titan-tg1-large'                                                                     ]
        assert list_set(models_anthropic__text    ) == ['anthropic.claude-instant-v1'     , 'anthropic.claude-v2'         , bug_in__anthropic__text                                                                       ]
        assert list_set(models_cohere___text      ) == ['cohere.command-light-text-v14'   , 'cohere.command-text-v14'     ,                                                                                               ]
        assert list_set(models_cohere___embedding ) == ['cohere.embed-english-v3'         , 'cohere.embed-multilingual-v3'                                                                                                ]
        assert list_set(models_meta__text         ) == ['meta.llama2-13b-chat-v1'         ,  'meta.llama2-70b-chat-v1'                                                                                                    ]
        assert list_set(models_stability_ai__image) == ['stability.stable-diffusion-xl-v1'                                                                                                                                ]


    def test_models_active__provisioned(self):
        active_models = self.bedrock.models_active()
        assert list_set(active_models) == ['ON_DEMAND', 'PROVISIONED']

        models                     = active_models.get('PROVISIONED')
        models_amazon              = models.get('Amazon'      )
        models_amazon__embedding   = models.get('Amazon'      ).get('EMBEDDING')
        models_amazon__image       = models.get('Amazon'      ).get('IMAGE'    )
        models_amazon__text        = models.get('Amazon'      ).get('TEXT')
        models_anthropic           = models.get('Anthropic'   )
        models_anthropic__text     = models.get('Anthropic'   ).get('TEXT')
        models_cohere              = models.get('Cohere'      )
        models_cohere___text       = models.get('Cohere'      ).get('TEXT')
        models_meta                = models.get('Meta'        )
        models_meta__text          = models.get('Meta'        ).get('TEXT')
        models_stability_ai        = models.get('Stability AI')
        models_stability_ai__image = models.get('Stability AI').get("IMAGE")

        assert list_set(models                    ) == ['Amazon', 'Anthropic', 'Cohere', 'Meta', 'Stability AI']
        assert list_set(models_amazon             ) == ['EMBEDDING', 'IMAGE', 'TEXT'   ]
        assert list_set(models_anthropic          ) == ['TEXT'                         ]
        assert list_set(models_cohere             ) == [ 'TEXT'                        ]
        assert list_set(models_meta               ) == ['TEXT'                         ]
        assert list_set(models_stability_ai       ) == ['IMAGE'                        ]

        bug_missing__in_anthropic__text = 'anthropic.claude-v2:1'           # BUG

        assert list_set(models_amazon__embedding  ) == [ 'amazon.titan-embed-image-v1:0'     , 'amazon.titan-embed-text-v1:2:8k'                                                                                               ]
        assert list_set(models_amazon__image      ) == [ 'amazon.titan-image-generator-v1:0'                                                                                                                                   ]
        assert list_set(models_amazon__text       ) == [ 'amazon.titan-text-express-v1:0:8k'  , 'amazon.titan-text-lite-v1:0:4k'                                                                                               ]
        assert list_set(models_anthropic__text    ) == [ 'anthropic.claude-instant-v1:2:100k' , 'anthropic.claude-v2:0:100k'    , 'anthropic.claude-v2:0:18k'       , 'anthropic.claude-v2:1:18k', 'anthropic.claude-v2:1:200k']
        assert list_set(models_cohere___text      ) == [ 'cohere.command-light-text-v14:7:4k' , 'cohere.command-text-v14:7:4k'                                                                                                 ]
        assert list_set(models_meta__text         ) == [ 'meta.llama2-13b-chat-v1:0:4k'                                                                                                                                        ]
        assert list_set(models_stability_ai__image) == [ 'stability.stable-diffusion-xl-v1:0'                                                                                                                                  ]

        # Note models with 'inferenceTypesSupported': [],
        #    - meta.llama2-13b-v1
        #    - meta.llama2-13b-v1:0:4k
        #    - meta.llama2-70b-chat-v1:0:4k
        #    - meta.llama2-70b-v1
        #    - meta.llama2-70b-v1:0:4k


    def test_models_by_throughput(self):
        on_demand_models   = self.bedrock.models_by_throughput__on_demand()
        provisioned_models =  self.bedrock.models_by_throughput__provisioned()
        assert len(on_demand_models  ) == 25
        assert len(provisioned_models) == 14



