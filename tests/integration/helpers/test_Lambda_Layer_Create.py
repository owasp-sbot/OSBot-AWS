import sys
from contextlib import contextmanager
from unittest import TestCase

from dotenv import load_dotenv
from osbot_aws.AWS_Config import AWS_Config

from osbot_aws.apis.Lambda_Layer import Lambda_Layer
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import parent_folder, current_temp_folder, folder_name, file_name, folder_exists, \
    folder_sub_folders
from osbot_utils.utils.Misc import random_text, wait_for

from osbot_aws.helpers.Lambda_Layer_Create import Lambda_Layer_Create, Lambda_Layers_Local



class test_Lambda_Layer_Create(TestCase):

    def setUp(self) -> None:
        self.layer_name          = random_text('layer_name_')
        self.lambda_layers_local = Lambda_Layers_Local()
        self.lambda_layer_create = Lambda_Layer_Create(layer_name=self.layer_name)

    def tearDown(self) -> None:
        self.lambda_layer_create.layer_folder_delete()
        assert self.lambda_layer_create.layer_folder_exists() is False

    def test__init__(self):
        assert self.lambda_layer_create.target_aws_lambda is True

        #assert self.lambda_layer_create.layer_name     == self.layer_name

    def test_path_layer_folder(self):
        path_layer_folder = self.lambda_layer_create.path_layer_folder()
        assert parent_folder(path_layer_folder) == self.lambda_layer_create.path_lambda_dependencies()
        assert folder_exists(path_layer_folder) is False

    def test_install_dependency(self):
        test_package = 'termcolor'
        result = self.lambda_layer_create.install_dependency(test_package)
        assert result.get('exists'   ) is True
        assert result.get('installed') is True
        assert 'Successfully installed termcolor' in result.get('output')

        assert self.lambda_layer_create.installed_packages() == {test_package: '2.3.0'}
        assert self.lambda_layer_create.has_package_installed(test_package) is True


    def test_execution_in_temp_layer(self):
        test_package     = 'termcolor'                                                                          # package to install
        layer__termcolor = Lambda_Layer_Create('layer_termcolor')                                           # create layer object for package
        if layer__termcolor.has_package_installed(test_package) is False:                                   # if layer doesn't have package
            assert layer__termcolor.install_dependency(test_package).get('installed') is True               # install package
        assert layer__termcolor.has_package_installed(test_package) is True                                 # confirm package is installed

        path_layer_folder = layer__termcolor.path_layer_folder()                                            # get path to layer folder
        try:
            import termcolor                                                                                # confirm package is not available
            raise Exception("termcolor is available")                                                       # we should never get here
        except ModuleNotFoundError:
            pass                                                                                            # this is expected path

        @contextmanager
        def add_to_sys_path(path):                                                                          # helper method to add path to sys.path
            sys.path.append(path)
            try:
                yield
            finally:
                sys.path.remove(path)


        with add_to_sys_path(path_layer_folder):                                                            # use context manager to add path to sys.path
            # noinspection PyUnresolvedReferences
            from termcolor import colored                                                                   # this import should now work since the path is in sys.path
            assert colored('Hello, World!', 'red', force_color=True) == '\x1b[31mHello, World!\x1b[0m'      # confirm that the import works
            assert path_layer_folder in sys.path                                                            # assert that the path is in sys.path
        assert path_layer_folder not in sys.path                                                                # assert that the path is no longer in sys.path

        #load_dotenv()
        layer_name   = f'test_lambda_layer_for_{test_package}'
        lambda_layer = Lambda_Layer(layer_name=layer_name)
        #result = lambda_layer.create_from_folder_via_s3(path_layer_folder)
        #pprint(result)

        # lambda_layer = Lambda_Layer()
        # layers = lambda_layer.layers(index_by='LayerName')
        # pprint(layers)




