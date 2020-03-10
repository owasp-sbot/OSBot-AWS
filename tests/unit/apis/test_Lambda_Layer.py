import os
from unittest import TestCase
from datetime import datetime

import gw_bot
from osbot_aws.Globals                                       import Globals
from gw_bot.helpers.Test_Helper                              import Test_Helper
from osbot_aws.apis.Lambda                                   import Lambda
from osbot_aws.apis.Lambda_Layer                             import Lambda_Layer
from osbot_utils.utils.Files                                 import Files
from osbot_aws.apis.test_helpers.Temp_Folder_With_Lambda_File import Temp_Folder_With_Lambda_File


class test_Lambda_Layer(Test_Helper):

    def setUp(self):
        super().setUp()
        #self.source_path      = os.path.dirname(gw_bot.__file__)[0:-8] + "../modules/sdk-eval-toolset/libraries/linux"        # todo: move to dedicated class
        #self.folders_mapping  = { self.source_path: 'lib/sdk-eval-toolset'}


        #self.api              = Lambda_Layer(layer_name="glasswall_editor_engine", folders_mapping = self.folders_mapping, s3_bucket=f'gw-bot-test-layer-bucket-{datetime.now().timestamp()}')

    def test_setUp(self):
        Files.exists(self.source_path)

    def test_create_from_zip_bytes(self):
        with Temp_Folder_With_Lambda_File('file_in_layer') as temp_folder:
            params     = { 'layer_name'          : 'test_simple_layer'   ,
                           'description'         : 'this is a test layer',
                           'runtimes'            : ['python3.8']         }

            lambda_layer = Lambda_Layer(**params)
            result = lambda_layer.create_from_zip_bytes(temp_folder.zip_bytes())

            layer_name = params.get('layer_name')
            region     = Globals.aws_session_region_name
            account_id = Globals.aws_session_account_id
            assert set(result)                      == { 'CompatibleRuntimes', 'Content', 'CreatedDate', 'Description', 'LayerArn', 'LayerVersionArn', 'Version'}
            assert result.get('LayerArn'          ) == f'arn:aws:lambda:{region}:{account_id}:layer:{layer_name}'
            assert result.get('Description'       ) == params.get('description')
            assert result.get('CompatibleRuntimes') == params.get('runtimes')

            self.result = result
        return




        layer = 'arn:aws:lambda:eu-west-1:311800962295:layer:test_simple_layer'

        #with Temp_Lambda() as _:
        #    _.delete_on_exit= False
        #    self.result = _.lambda_name
        lambda_name ='temp_lambda_YRWKWQ'
        temp_lambda = Lambda(lambda_name)
        temp_lambda.configuration_update(Layers=[f'{layer}:1'])

        #self.result = temp_lambda.info()
        self.result = temp_lambda.invoke({})


        #self.folder.delete()



    #def test_create_lambda_layer(self):
    #    self.assertEqual(type(self.api.create()), str)
    #    self.assertEqual(self.api.delete(with_s3_bucket=True), True)


    # todo: make this test more robust since at the moment this depends on the layers below existing in the current AWS environment
    def test_layers(self):
        lambda_layer = Lambda_Layer()
        assert lambda_layer.layers()                     == [ { 'LatestMatchingVersion': { 'CompatibleRuntimes'    : ['python3.8']                                                     ,
                                                                                           'CreatedDate'           : '2020-02-20T01:21:20.895+0000'                                    ,
                                                                                           'Description'           : 'this is a test layer'                                            ,
                                                                                           'LayerVersionArn'       : 'arn:aws:lambda:eu-west-1:311800962295:layer:test_simple_layer:1' ,
                                                                                           'Version'               : 1                                                                },
                                                                'LayerArn' : 'arn:aws:lambda:eu-west-1:311800962295:layer:test_simple_layer'                                           ,
                                                                'LayerName': 'test_simple_layer'                                                                                      }]

        assert lambda_layer.layers(index_by='LayerName') == { 'test_simple_layer': { 'LatestMatchingVersion': { 'CompatibleRuntimes': [ 'python3.8'],
                                                                                                                'CreatedDate': '2020-02-20T01:21:20.895+0000',
                                                                                                                'Description': 'this is a test layer',
                                                                                                                'LayerVersionArn': 'arn:aws:lambda:eu-west-1:311800962295:layer:test_simple_layer:1',
                                                                                                                'Version': 1},
                                                                                      'LayerArn' : 'arn:aws:lambda:eu-west-1:311800962295:layer:test_simple_layer',
                                                                                      'LayerName': 'test_simple_layer'}}

        #


    def test_mutable_init_value(self):
        assert Lambda_Layer(folders_mapping={'a':42}).folders_mapping == {'a':42}
        assert Lambda_Layer(                        ).folders_mapping == {}
        assert Lambda_Layer(folders_mapping={'b':-1}).folders_mapping == {'b':-1}
        assert Lambda_Layer(                        ).folders_mapping == {}


    def test_mutable_value_on_function(self):
        def func(key, value, a={}):
            a[key] = value
            return a
        assert func('a', 10) == {'a': 10}           # that's expected
        assert func('b', 20) == {'a': 10, 'b': 20}  # that could be unexpected



