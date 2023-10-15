from osbot_aws.apis.Lambda_Layer import Lambda_Layer

from osbot_utils.utils.Process  import Process
from osbot_utils.utils.Files import current_temp_folder, path_combine, folder_create, folder_sub_folders, folders_names, \
    folder_exists, folder_delete_recursively

from osbot_aws.helpers.Lambda_Layers_Local import Lambda_Layers_Local

class Lambda_Layer_Create:

    def __init__(self, layer_name):
        self.layer_name          = layer_name
        self.lambda_layer        = Lambda_Layer(self.layer_name)
        self.lambda_layers_local = Lambda_Layers_Local()
        self.target_aws_lambda   = True

    def add_package(self, package_name):
        if self.has_package_installed(package_name):
            exists    = True
            installed = False
            output    = ''
        else:
            target_folder = self.path_layer_folder()
            args          = ['install']
            if self.target_aws_lambda:
                args.extend(['--platform','manylinux1_x86_64', '--only-binary=:all:'])
            args.extend(['-t', target_folder, package_name])

            result      = Process.run('pip3', args)
            exists      = result.get('status') == 'ok'
            installed   = True
            output      = result.get('stdout')

        return  dict( exists    = exists    ,
                      installed = installed ,
                      output    = output    )

    def add_packages(self, packages):
        results = {}
        for package in packages:
            result = self.add_package(package)
            results[package] = result
        return results

    def arn_latest(self):
        return self.lambda_layer.arn_latest()

    def create(self, skip_if_exists=True):
        if skip_if_exists and self.exists():
            return self.arn_latest()
        return self.lambda_layer.create_from_folder_via_s3(self.path_layer_folder())

    def delete(self):
        return self.lambda_layer.delete()

    def exists(self):
        return self.lambda_layer.exists()

    def has_package_installed(self, package_name):
        return package_name in self.installed_packages()


    def installed_packages(self):
        folders = folder_sub_folders(self.path_layer_folder())

        # Dictionary to store package names and versions
        package_dict = {}

        for folder in folders:
            # Split path to get package name and version info
            parts = folder.split('/')
            name = parts[-1]

            # Check for package version info
            if name.endswith('.dist-info'):
                package_name = name.split('-')[0]
                version = name.split('-')[1].replace('.dist', '').split('.dist-info')[0]
                package_dict[package_name] = version
            else:
                if name not in package_dict:
                    package_dict[name] = None

        return package_dict

    def layer_folder_create(self):
        return folder_create(self.path_layer_folder())

    def layer_folder_delete(self):
        return folder_delete_recursively(self.path_layer_folder())

    def layer_folder_exists(self):
        return folder_exists(self.path_layer_folder())

    def path_lambda_dependencies(self):
        return self.lambda_layers_local.path_lambda_dependencies()

    def path_layer_folder(self):
        return path_combine(self.lambda_layers_local.path_lambda_dependencies(), self.layer_name)

