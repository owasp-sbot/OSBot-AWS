import sys
from contextlib import contextmanager
from unittest import TestCase

from dotenv import load_dotenv
from osbot_utils.utils.Dev import pprint

from osbot_aws.apis.test_helpers.Temp_Lambda import Temp_Lambda
from osbot_utils.utils.Files import parent_folder, current_temp_folder, folder_name, file_name, folder_exists, \
    folder_sub_folders, files_list, files_names
from osbot_utils.utils.Misc import random_text, wait_for

from osbot_aws.helpers.Lambda_Layer_Create import Lambda_Layer_Create, Lambda_Layers_Local
from osbot_utils.utils.Temp_Sys_Path import Temp_Sys_Path


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

    def test_add_package(self):
        test_package = 'termcolor'
        result = self.lambda_layer_create.add_package(test_package)
        assert result.get('exists'   ) is True
        assert result.get('installed') is True
        assert 'Successfully installed termcolor' in result.get('output')

        installed_packages = self.lambda_layer_create.installed_packages()
        assert test_package in installed_packages
        assert result       == installed_packages.get(test_package)
        assert self.lambda_layer_create.has_package_installed(test_package) is True

    def test_path_path_installed_packages(self):
        path_installed_packages = self.lambda_layer_create.path_installed_packages()
        assert parent_folder(path_installed_packages) == self.lambda_layer_create.path_layer_folder()
        assert file_name    (path_installed_packages) == 'installed_packages.json'

    def test_path_layer_folder(self):
        path_layer_folder = self.lambda_layer_create.path_layer_folder()
        assert parent_folder(path_layer_folder) == self.lambda_layer_create.path_lambda_dependencies()
        assert folder_exists(path_layer_folder) is False

    def test_update_installed_packages(self):
        package_name = 'an_package'
        data         = {'answer': 42}
        assert 'installed_packages.json' not in files_names(files_list(self.lambda_layer_create.path_layer_folder()))
        assert package_name not in self.lambda_layer_create.installed_packages()
        assert self.lambda_layer_create.update_installed_packages(package_name, data) == {package_name: data}
        assert self.lambda_layer_create.installed_packages()                          == {package_name: data}
        assert '_osbot_installed_packages.json' in files_names(files_list(self.lambda_layer_create.path_layer_folder()))

    def test_2n2__execution_in_temp_layer(self):
        test_package     = 'termcolor'                                                                          # package to install
        layer__termcolor = Lambda_Layer_Create('layer_termcolor')                                           # create layer object for package
        if layer__termcolor.has_package_installed(test_package) is False:                                   # if layer doesn't have package
            assert layer__termcolor.add_package(test_package).get('installed') is True               # install package
        assert layer__termcolor.has_package_installed(test_package) is True                                 # confirm package is installed

        path_layer_folder = layer__termcolor.path_layer_folder()                                            # get path to layer folder
        try:
            # noinspection PyUnresolvedReferences,PyPackageRequirements
            import termcolor                                                                                # confirm package is not available
            raise Exception("termcolor is available")                                                       # we should never get here
        except ModuleNotFoundError:
            pass                                                                                            # this is expected path

        with Temp_Sys_Path(path_layer_folder):                                                            # use context manager to add path to sys.path
            # noinspection PyUnresolvedReferences,PyPackageRequirements
            from termcolor import colored                                                                   # this import should now work since the path is in sys.path
            assert colored('Hello, World!', 'red', force_color=True) == '\x1b[31mHello, World!\x1b[0m'      # confirm that the import works
            assert path_layer_folder in sys.path                                                            # assert that the path is in sys.path
        assert path_layer_folder not in sys.path                                                                # assert that the path is no longer in sys.path

        layer_arn = layer__termcolor.arn_latest()
        if layer_arn is None:
            layer_arn = layer__termcolor.create()
            assert layer_arn == layer__termcolor.arn_latest()

        # temp lambda code
        def run(event, context):
            # noinspection PyUnresolvedReferences,PyPackageRequirements
            import termcolor
            return f'OSBot inside an Lambda :).... {termcolor}'


        with Temp_Lambda(lambda_code=run, with_layer=layer_arn) as temp_lambda:
            lambda_info = temp_lambda.info()
            assert lambda_info.get('Configuration').get('Layers') == [{'Arn': layer_arn, 'CodeSize': 7914}]
            assert temp_lambda.invoke() == "OSBot inside an Lambda :).... <module 'termcolor' from '/opt/python/termcolor/__init__.py'>"

        assert layer__termcolor.lambda_layer.delete() is True       # delete layer in AWS
        assert layer__termcolor.layer_folder_delete() is True       # delete layer locally

        assert layer__termcolor.exists              () is False     # confirm layer doesn't exist in AWS
        assert layer__termcolor.arn_latest          () is None      # confirm that there is no active layer in AWS
        assert layer__termcolor.layer_folder_exists () is False     # confirm that the layer folder doesn't exist locally


