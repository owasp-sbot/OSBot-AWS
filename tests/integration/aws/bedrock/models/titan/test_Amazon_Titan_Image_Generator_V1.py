import pytest

from osbot_aws.aws.bedrock.models.titan.Amazon_Titan_Image_Generator_V1 import Amazon_Titan_Image_Generator_V1
from osbot_aws.testing.TestCase__Bedrock                                import TestCase__Bedrock
from osbot_utils.utils.Env                                              import in_github_action
from osbot_utils.utils.Misc                                             import list_set


class test_Amazon_Titan_Image_Generator_V1(TestCase__Bedrock):

    def setUp(self):
        if in_github_action():                                  # disabling Bedrock tests in GitHub actions since they are not 100% deterministic
            pytest.skip()
        self.model    = Amazon_Titan_Image_Generator_V1()
        self.png_data = None

    def tearDown(self):
        if self.png_data:
            target_file = '/tmp/titan_image.png'
            self.model.save_png_data(png_data=self.png_data, target_file=target_file)

    def test_body__image_variation(self):
        #image_request_hash     = '4eaafd075a2adde25c26117c000972b4f0af2ed1b52390044a87321aabe74582'     #  big X         : 4th in test_body__text_image below
        #image_request_hash     = '15f6a9afac93bf760077c584aa4c0fac4874f3936fc74307a9b6a30f1feac5b1'     #  old house     : 6th in test_body__text_image below
        image_request_hash     = '21152f6746c5c4955e61883154623403a66bebc8eb9617c3775c9b10f1fd0e9c'      #  'green iguana': 7th in test_body__text_image below
        response_data_for_hash = self.cache.response_data_for__request_hash(image_request_hash)
        image_base_64          = response_data_for_hash.get('images')[0]
        model_id               = self.model.model_id
        images                 = [image_base_64]
        prompt_to_use          = 6
        model                  = self.model
        test_prompts           = [{"prompt"         : "change X to an Y",
                                   "negative_text"  : "",
                                   "comments"       : "didn't work"     },          # todo: add these comments to the response row
                                  {"prompt"         : "only change the X",
                                   "negative_text"  : ""                ,
                                   "comments"       : "didn't work"    },
                                  {"prompt"         : "only change the X",
                                   "negative_text"  : ""                ,
                                   "comments": "didn't work"            },          # todo: add these comments to the response row
                                  {"prompt"         : "don't change the X",
                                   "negative_text": ""                  ,
                                   "comments"       : "didn't work"     },          # todo: add these comments to the response row}
                                  {"prompt"         : "Modernize the house, photo-realistic, 8k, hdr",             # using prompt from https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-titan-image.html#model-parameters-titan-image-code-examples
                                   "negative_text"  : "bad quality, low resolution, cartoon"         ,
                                   "comments"       : ""                                             },
                                  {"prompt"         : "Change to a very tall house, photo-realistic, 8k, hdr",
                                   "negative_text"  : "bad quality, low resolution, cartoon"         ,
                                   "comments"       : ""                                             },
                                  {"prompt"         : "small crocodile",
                                   "negative_text"  : "",
                                   "comments"       : "worked ok"}]
        model.text             = test_prompts[prompt_to_use].get('prompt')
        model.negative_text    = test_prompts[prompt_to_use].get('negative_text')
        body__image_variation  = self.model.body__image_variation(images)
        #pprint(body__image_variation)
        response = self.bedrock.model_invoke(model_id, body__image_variation)
        assert list_set(response) == ['error', 'images']
        error       = response.get('error')
        images      = response.get('images')
        self.png_data    = images.pop()
        assert error is None
        assert len(self.png_data) > 30000

    def test_body__in_painting(self):
        #self.cache.disable()
        image_request_hash    = 'af617d164a55204ef0e0c1fefe928aff5c73cc8fe941b36c25fbfaea5f3b5833'       # 'man on bench  : 8th in test_body__text_image below
        response_data_for_hash = self.cache.response_data_for__request_hash(image_request_hash)
        image_base_64          = response_data_for_hash.get('images')[0]
        model_id               = self.model.model_id
        prompt_to_use          = 0
        model                  = self.model
        test_prompts           = [{"prompt"         : "two women"    ,            # using prompt from https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-titan-image.html#model-parameters-titan-image-code-examples
                                   "mask_prompt"    : "person"       ,
                                   "negative_text"  : "",
                                   "comments"       : ""             },
                                  ]
        model.text             = test_prompts[prompt_to_use].get('prompt')
        model.negative_text    = test_prompts[prompt_to_use].get('negative_text')
        mask_prompt            = test_prompts[prompt_to_use].get('mask_prompt')
        body__inpainting       = self.model.body__in_painting(image_base_64, mask_prompt)

        response = self.bedrock.model_invoke(model_id, body__inpainting)
        assert list_set(response) == ['error', 'images']
        error       = response.get('error')
        images      = response.get('images')
        self.png_data    = images.pop()
        assert error is None
        assert len(self.png_data) > 30000

    def test_body__out_painting(self):
        #self.cache.disable()
        image_request_hash    = 'af617d164a55204ef0e0c1fefe928aff5c73cc8fe941b36c25fbfaea5f3b5833'       # 'man on bench  : 8th in test_body__text_image below
        response_data_for_hash = self.cache.response_data_for__request_hash(image_request_hash)
        image_base_64          = response_data_for_hash.get('images')[0]
        model_id               = self.model.model_id
        prompt_to_use          = 0
        model                  = self.model
        test_prompts           = [{"prompt"         : "sea with beach and boats" ,            # using prompt from https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-titan-image.html#model-parameters-titan-image-code-examples
                                   "mask_prompt"    : "person"                    ,
                                   "negative_text"  : ""                          ,
                                   "comments"       : ""                          },
                                  ]
        model.text             = test_prompts[prompt_to_use].get('prompt')
        model.negative_text    = test_prompts[prompt_to_use].get('negative_text')
        mask_prompt            = test_prompts[prompt_to_use].get('mask_prompt')
        body__out_painting       = self.model.body__out_painting(image_base_64, mask_prompt)

        response = self.bedrock.model_invoke(model_id, body__out_painting)
        assert list_set(response) == ['error', 'images']
        error       = response.get('error')
        images      = response.get('images')
        self.png_data    = images.pop()
        assert error is None
        assert len(self.png_data) > 30000


    def test_body__text_image(self):
        prompt_to_use = 8
        test_prompts =  [{"prompt"       : "A photograph of a cup of coffee from the side, with a dog drinking that coffee",
                          "negative_text": "" ,
                          "comment"      : "shows picture of dog drinking that coffee with the cup of coffee on top of a table"},
                         {"prompt"       : "A photograph of a cup of coffee from the side, with a dog drinking that coffee",
                          "negative_text": "table" ,
                          "comment"      : "negative text had no effect, table is still there"},
                         {"prompt"       : "A photograph of a cup of coffee from the side, with a dog drinking that coffee",
                          "negative_text": "black dogs" ,
                          "comment"      : "this worked, now we got a brown dog"},
                         {"prompt"       : "A photograph of a cup of coffee from the side, with a dog drinking that coffee",
                          "negative_text": "black or brown dogs" ,
                          "comment"      : "this didn't work very well, since now we got what it looks like a black dog"},
                         {"prompt"       : "a big X",
                          "negative_text": "" ,
                          "comment"      : "Here we get a big X"},
                         {"prompt"       : "a big X",
                          "negative_text": "blue" ,
                          "comment"      : "This didn't work since I was trying to remove the blue background"},
                         {"prompt"       : "an old house",
                          "negative_text": "" ,
                          "comment"      : ""},
                         {"prompt"       : 'a green iguana',            # from AWS Pdf: Amazon Titan Image Generator Prompt Engineering Best Practices
                         'negative_text' : ''              },
                         {"prompt"       : 'man sitting on a bench facing the camera',
                          'negative_text': 'got man on bench but not with face to the camera'}
                         ]


        self.model.text          = test_prompts[prompt_to_use].get('prompt')         # set the prompt text
        self.model.negative_text = test_prompts[prompt_to_use].get('negative_text')  # set the negative text
        model_id                 = self.model.model_id                               # get the model_id (in this case 'amazon.titan-image-generator-v1')
        body__text_image         = self.model.body__text_image()                     # get the json data for this model

        text_to_image_params = {"text": self.model.text}                             # replicate the validation login
        if self.model.negative_text and len(self.model.negative_text) > 3:           # or it will fail AWS validation
            text_to_image_params["negativeText"] = self.model.negative_text

        assert model_id             == 'amazon.titan-image-generator-v1'
        assert body__text_image     == {'imageGenerationConfig': { 'cfgScale'      : 10.0         ,
                                                       'height'        : 512          ,
                                                       'numberOfImages': 1            ,
                                                       'seed'          : 42           ,
                                                       'width'         : 512          },
                                        'taskType'            :  'TEXT_IMAGE'                    ,
                                        'textToImageParams'   : text_to_image_params             }

        response        = self.bedrock.model_invoke(model_id, body__text_image)         # invoke model using OSBot_AWS Bedrock api

        assert list_set(response) == ['error', 'images']
        error       = response.get('error')
        images      = response.get('images')
        self.png_data    = images.pop()
        assert error is None
        assert len(self.png_data) > 30000        # was first 513424 then 520564

