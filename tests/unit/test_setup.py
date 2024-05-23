import importlib
import os
from importlib.util import spec_from_file_location, module_from_spec

from osbot_utils.utils.Dev import pprint

import osbot_aws
import setuptools                   # this is needed for @patch('setuptools.setup')
from unittest                       import TestCase
from unittest.mock                  import patch
from osbot_utils.utils.Files        import parent_folder
from osbot_aws.utils.Version        import Version

EXPECTED_PACKAGES = ['osbot_aws'                                        ,
                     'osbot_aws.apis'                                   ,
                     'osbot_aws.apis.shell'                             ,
                     'osbot_aws.apis.test_helpers'                      ,
                     'osbot_aws.aws'                                    ,
                     'osbot_aws.aws.apigateway'                         ,
                     'osbot_aws.aws.apigateway.apigw_dydb'              ,
                     'osbot_aws.aws.apigateway.lambdas'                 ,
                     'osbot_aws.aws.bedrock'                            ,
                     'osbot_aws.aws.bedrock.cache'                      ,
                     'osbot_aws.aws.bedrock.cache.html'                 ,
                     'osbot_aws.aws.bedrock.models'                     ,
                     'osbot_aws.aws.bedrock.models.ai21'                ,
                     'osbot_aws.aws.bedrock.models.claude'              ,
                     'osbot_aws.aws.bedrock.models.command'             ,
                     'osbot_aws.aws.bedrock.models.diffusion'           ,
                     'osbot_aws.aws.bedrock.models.llama2'              ,
                     'osbot_aws.aws.bedrock.models.mistral'             ,
                     'osbot_aws.aws.bedrock.models.titan'               ,
                     'osbot_aws.aws.bedrock.models.titan.base_classes'  ,
                     'osbot_aws.aws.boto3'                              ,
                     'osbot_aws.aws.dynamo_db'                          ,
                     'osbot_aws.aws.dynamo_db.domains'                  ,
                     'osbot_aws.aws.dynamo_db.models'                   ,
                     'osbot_aws.aws.ecs'                                ,
                     'osbot_aws.aws.iam'                                ,
                     'osbot_aws.aws.lambda_'                            ,
                     'osbot_aws.aws.route_53'                           ,
                     'osbot_aws.aws.s3'                                 ,
                     'osbot_aws.aws.sts'                                ,
                     'osbot_aws.decorators'                             ,
                     'osbot_aws.deploy'                                 ,
                     'osbot_aws.exceptions'                             ,
                     'osbot_aws.helpers'                                ,
                     'osbot_aws.lambdas'                                ,
                     'osbot_aws.lambdas.dev'                            ,
                     'osbot_aws.lambdas.pocs'                           ,
                     'osbot_aws.lambdas.shell'                          ,
                     'osbot_aws.testing'                                ,
                     'osbot_aws.utils'                                  ]

class test_setup(TestCase):


    @patch('setuptools.setup')                                                            # this prevents the sys.exit() from being called
    def test_setup(self, mock_setup):
        parent_path     = parent_folder(osbot_aws.path)                                   # get the root of the repo
        setup_file_path = os.path.join(parent_path, 'setup.py')                           # get the setup.py file
        assert os.path.exists(setup_file_path)                                            # make sure it exists

        os.chdir(parent_path)                                                             # change current directory to root so that the README.me file can be resolved
        spec     = spec_from_file_location("some.module.name", setup_file_path)     # do this dynmamic load so that we find the correct setup file
        setup    = module_from_spec(spec)
        spec.loader.exec_module(setup)

        args, kwargs = mock_setup.call_args                                                # capture the params used on the setup call
        assert kwargs.get('name') == 'osbot_aws'
        assert kwargs.get('description'     ) == 'OWASP Security Bot - AWS'
        assert kwargs.get('long_description') == setup.long_description
        assert kwargs.get('version'         ) == Version().value()
        assert sorted(kwargs.get('packages' )) == sorted(EXPECTED_PACKAGES)