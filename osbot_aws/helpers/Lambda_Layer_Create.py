from osbot_utils.utils.Misc             import list_set
from osbot_utils.utils.Json             import json_save_file, json_load_file
from osbot_aws.aws.lambda_.Lambda_Layer import Lambda_Layer
from osbot_utils.utils.Process          import Process
from osbot_utils.utils.Files            import path_combine, folder_create, folder_sub_folders, folders_names, \
    folder_exists, folder_delete_recursively, file_exists

from osbot_aws.helpers.Lambda_Layers_Local import Lambda_Layers_Local

class Lambda_Layer_Create:

    FILE_INSTALLED_PACKAGES = '_osbot_installed_packages.json'

    def __init__(self, layer_name):
        self.layer_name          = layer_name
        self.lambda_layer        = Lambda_Layer(self.layer_name)
        self.lambda_layers_local = Lambda_Layers_Local()
        self.target_aws_lambda   = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def add_package(self, package):
        if type(package) is dict:
            if 'name' not in package:
                return {'error'    : 'missing name property in package_name dict',
                        'installed': False                             ,         }
            package_name      = package.get('name')
            target_aws_lambda = package.get('target_aws_lambda', True)
        else:
            package_name      = package
            target_aws_lambda = self.target_aws_lambda

        installed_package = self.installed_packages().get(package_name)
        if installed_package:
            return installed_package

        target_folder = self.path_layer_folder()
        args          = ['install']
        if target_aws_lambda:
            args.extend(['--platform','manylinux1_x86_64', '--only-binary=:all:'])
        args.extend(['-t', target_folder, package_name])

        result      = Process.run('pip3', args)
        output      = result.get('stdout')
        error       = result.get('stderr')
        exists      = result.get('status') == 'ok' and  ('ERROR' in error)  # todo: add better detection to see if package was installed ok
        installed   = True
        result      = dict(exists            = exists           ,
                           installed         = installed        ,
                           name              = package_name     ,
                           output            = output           ,
                           error             = error            ,
                           target_aws_lambda = target_aws_lambda)

        self.update_installed_packages(package_name, result)
        return result

    def add_packages(self, packages):
        results = {}
        for package in packages:
            package      = self.add_package(package)
            package_name = package.get('name')
            results[package_name] = package
        return results

    def arn_latest(self):
        return self.lambda_layer.arn_latest()

    def create(self, skip_if_exists=True):
        if skip_if_exists and self.exists():
            return self.arn_latest()
        return self.lambda_layer.create_from_folder_via_s3(self.path_layer_folder())

    def delete_layer(self):
        return self.lambda_layer.delete()

    def delete_local_layer_folder(self):
        return self.layer_folder_delete()

    def exists(self):
        return self.lambda_layer.exists()

    def has_package_installed(self, package_name):
        return package_name in self.installed_packages()


    def installed_packages(self):
        path_installed_packages = self.path_installed_packages()
        return json_load_file(path_installed_packages)
        # todo: add detection of which folders (and maybe even files) were modified on the installation
        # todo: add back the feature below to extract the versions of the packages installed from the .dist file
        #
        # folders = folder_sub_folders(self.path_layer_folder())
        #
        # # Dictionary to store package names and versions
        # package_dict = {}
        #
        # for folder in folders:
        #     # Split path to get package name and version info
        #     parts = folder.split('/')
        #     name = parts[-1]
        #
        #     # Check for package version info
        #     if name.endswith('.dist-info'):
        #         package_name = name.split('-')[0]
        #         version = name.split('-')[1].replace('.dist', '').split('.dist-info')[0]
        #         package_dict[package_name] = version
        #     else:
        #         if name not in package_dict:
        #             package_dict[name] = None

        # return package_dict

    def installed_packages_names(self):
        return list_set(self.installed_packages())

    def installed_packages_reset(self):
        if file_exists(self.path_installed_packages()):
            json_save_file({}, self.path_installed_packages())
        self.delete_local_layer_folder()
        self.layer_folder_create()
        return self

    def layer_folder_create(self):
        return folder_create(self.path_layer_folder())

    def layer_folder_delete(self):
        return folder_delete_recursively(self.path_layer_folder())

    def layer_folder_exists(self):
        return folder_exists(self.path_layer_folder())

    def path_installed_packages(self):
        return path_combine(self.path_layer_folder(), self.FILE_INSTALLED_PACKAGES)

    def path_lambda_dependencies(self):
        return self.lambda_layers_local.path_lambda_dependencies()

    def path_layer_folder(self):
        return path_combine(self.lambda_layers_local.path_lambda_dependencies(), self.layer_name)

    def recreate(self):
        return self.create(skip_if_exists=False)

    def update_installed_packages(self, package_name, data):
        installed_packages               = self.installed_packages()
        installed_packages[package_name] = data
        path_layer_folder                = self.path_layer_folder()
        path_installed_packages          = self.path_installed_packages()
        folder_create(path_layer_folder)                                        # make sure folder_exists
        json_save_file(installed_packages, path_installed_packages, pretty=True)             # save data into path_installed_packages file
        return installed_packages