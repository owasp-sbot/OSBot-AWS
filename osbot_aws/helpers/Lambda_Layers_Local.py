from osbot_utils.utils.Files import path_combine, current_temp_folder, folder_sub_folders, folders_names


class Lambda_Layers_Local:
    DEFAULT_TARGET_FOLDER_NAME = '_lambda_dependencies'

    def __init__(self):
        pass

    def path_lambda_dependencies(self):
        return path_combine(current_temp_folder(), self.DEFAULT_TARGET_FOLDER_NAME)

    def installed_layers(self):
        folders = folder_sub_folders(self.path_lambda_dependencies())
        return folders_names(folders)
