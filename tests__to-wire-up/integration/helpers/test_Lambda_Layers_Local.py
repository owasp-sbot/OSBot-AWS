from unittest import TestCase

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import current_temp_folder, file_name, parent_folder, folder_name

from osbot_aws.helpers.Lambda_Layer_Create import Lambda_Layer_Create
from osbot_aws.helpers.Lambda_Layers_Local import Lambda_Layers_Local


class test_Lambda_Layers_Local(TestCase):

    def setUp(self) -> None:
        self.lambda_layers_local = Lambda_Layers_Local()

    def test_path_lambda_dependencies(self):
        path_lambda_dependencies = self.lambda_layers_local.path_lambda_dependencies()
        assert parent_folder(path_lambda_dependencies) == current_temp_folder()
        assert folder_name  (path_lambda_dependencies) == self.lambda_layers_local.DEFAULT_TARGET_FOLDER_NAME

    def test_installed_layers(self):
        for installed_layer in self.lambda_layers_local.installed_layers():
            if installed_layer.startswith('layer_name_'):
                lambda_layer_create = Lambda_Layer_Create(layer_name=installed_layer)
                print(f"deleting layer {installed_layer}")
                assert lambda_layer_create.layer_folder_exists() is True
                assert lambda_layer_create.layer_folder_delete() is True
                assert lambda_layer_create.layer_folder_exists() is False