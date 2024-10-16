import os
import importlib
import site

from osbot_aws.aws.lambda_.Lambda_Layer         import Lambda_Layer
from osbot_utils.testing.Temp_Folder            import Temp_Folder
from osbot_utils.testing.Temp_Zip               import Temp_Zip
from osbot_utils.utils.Process                  import Process
from osbot_aws.AWS_Config                       import AWS_Config
from osbot_aws.apis.test_helpers.Temp_Aws_Roles import Temp_Aws_Roles
from osbot_utils.utils.Files                    import folder_copy, Files, folder_not_exists, path_combine, folder_name

from osbot_aws.aws.lambda_.Lambda import Lambda


class Lambda_Package:
    def __init__(self,lambda_name):
        self.lambda_name   = lambda_name
        self.aws_lambda    = Lambda(self.lambda_name)
        self.s3_bucket     = AWS_Config().lambda_s3_bucket()
        self.s3_key        = f'{AWS_Config().lambda_s3_folder_lambdas()}/{self.lambda_name}.zip'
        self.role_arn      = Temp_Aws_Roles().for_lambda_invocation__role_arn()
        self.tmp_folder    = Files.temp_folder('tmp_lambda_')
        self.layers        = []
        self.env_variables = {}
        (self.aws_lambda.set_s3_bucket   (self.s3_bucket    )
                        .set_s3_key      (self.s3_key       )
                        .set_role        (self.role_arn     )
                        .set_folder_code (self.tmp_folder  ))

    # helper methods
    @staticmethod
    def get_root_folder():
        return Files.path_combine(__file__, '../..')

    # Lambda class wrappers

    def create(self             ): return self.aws_lambda.create()
    def delete(self             ): return self.aws_lambda.delete()
    def invoke(self, params=None): return self.aws_lambda.invoke(params)
    def update(self             ): return self.aws_lambda.update()
    def reset (self             ): return self.aws_lambda.update_lambda_code()              # this will trigger a reset and force cold start on next execution

    # main methods
    def add_layer(self, layer_arn):
        self.aws_lambda.add_layer(layer_arn)

    def add_layers(self, layers_arn):
        for layer_arn in layers_arn:
            self.aws_lambda.add_layer(layer_arn)
        return self

    def add_file(self, source):
        Files.copy(source, self.tmp_folder)

    def add_folder(self, source, ignore=None):
        destination = Files.path_combine(self.tmp_folder, folder_name(source))
        if folder_not_exists(destination):
            folder_copy(source=source, destination=destination,ignore_pattern=ignore)
        self.remove_files('__pycache__')
        return self

    def add_module(self,module_name):
        module_path = importlib.import_module(module_name).__path__[0]     # get folder of module
        self.add_folder(module_path)                                       # add module's folder
        return self

    def add_modules(self, modules_names):
        for module_name in modules_names:
            self.add_module(module_name)
        return self

    def add_root_folder(self):
        self.add_folder(self.get_root_folder())
        return self

    def add_osbot_aws(self):
        self.add_osbot_utils()
        self.add_module('osbot_aws')

    def add_osbot_browser(self):
        self.add_module('osbot_browser')

    def add_osbot_elastic(self):
        self.add_module('osbot_elastic')

    def add_osbot_utils(self):
        self.add_module('osbot_utils')
        return self

    def arn(self):
        return self.aws_lambda.function_arn()

    def create_layer(self, target_folder, ignore_pattern=None):
        if ignore_pattern is None:
            ignore_pattern = ['*.pyc', '.DS_Store', '__pycache__', '.env']

        layer_name   = folder_name(target_folder)
        lambda_layer = Lambda_Layer(layer_name)
        with Temp_Folder() as _:
            source      = target_folder
            destination = path_combine(_.path() + '/python', folder_name(source))
            folder_copy(source=source, destination=destination, ignore_pattern=ignore_pattern)
            with Temp_Zip(_.path()) as zip_file:
                result = lambda_layer.create_from_zip_file_via_s3(zip_file.path())
                return  result.get('LayerVersionArn')

    def create_layer_from_packages(self, layer_name, packages, target_aws_lambda=True):
        # if ignore_pattern is None:
        #     ignore_pattern = ['*.pyc', '.DS_Store', '__pycache__', '.env']

        with Temp_Folder() as _:
            destination = path_combine(_.path(), 'python')
            for package in packages:
                args = ['install']
                if target_aws_lambda:
                    args.extend(['--platform', 'manylinux1_x86_64', '--only-binary=:all:'])
                args.extend(['-t', destination, package])
                Process.run('pip3', args)
            with Temp_Zip(_.path()) as zip_file:
                lambda_layer = Lambda_Layer(layer_name)
                result       = lambda_layer.create_from_zip_file_via_s3(zip_file.path())
                return result.get('LayerVersionArn')


    def create_layer_from_site_packages(self, target_name, ignore_pattern=None):
        if ignore_pattern is None:
            ignore_pattern = ['*.pyc', '.DS_Store', '__pycache__', '.env']

        with Temp_Folder() as _:
            layer_name   = f'site_packages__{target_name}'
            lambda_layer = Lambda_Layer(layer_name)
            source       = site.getsitepackages()[0]
            destination  = path_combine(_.path(), 'python')
            folder_copy(source=source, destination=destination, ignore_pattern=ignore_pattern)
            with Temp_Zip(_.path()) as zip_file:
                result = lambda_layer.create_from_zip_file_via_s3(zip_file.path())
                return  result.get('LayerVersionArn')

    def get_files(self):
        all_files = []
        for root, dirs, files in os.walk(self.tmp_folder):
            for file in files:
                file_path = Files.path_combine(root,file).replace(self.tmp_folder,'')
                all_files.append(file_path)
        return all_files


    def remove_files(self,pattern):
        for file in self.get_files():
            if pattern in file:
                file_to_delete = Files.path_combine(self.tmp_folder,file[1:])
                Files.delete(file_to_delete)

    def set_handler(self, handler):
        self.aws_lambda.set_handler(handler)
        return self

    def set_env_variable(self, key, value):
        self.aws_lambda.set_env_variable(key, value)
        return self

    def set_env_variables(self, env_variables):
        self.aws_lambda.set_env_variables(env_variables)
        return self

    def set_layers(self, layers):
        self.aws_lambda.set_layers(layers)
        return self

    def set_image_uri(self, image_uri):
        self.aws_lambda.image_uri = image_uri

    def use_lambda_file(self,lambda_file):
        file_path = Files.path_combine(self.get_root_folder(), lambda_file)
        if Files.exists(file_path) is False:
            return { 'status': 'error', 'data': 'could not find lambda file `{0}` in root folder `{1}`'.format(lambda_file, self.get_root_folder())}
        target_file = Files.path_combine(self.tmp_folder, '{0}.py'.format(self.lambda_name))
        Files.copy(file_path,target_file)
        return  { 'status': 'ok', 'file_path': file_path, 'target_file': target_file }

    def uses_image_uri(self):
        return self.aws_lambda.image_uri is not None

    def update_with_root_folder(self,delete_before=False):
        if delete_before:
            self.delete()
        self.add_root_folder()
        self.add_osbot_utils()
        self.update()
        return self

    def update_code(self):
        base_folder = self.lambda_name.split('.').pop(0)                    # will point to the top level module
        self.add_module(base_folder)                                        # add module's folder
        self.add_root_folder()                                              # add osbot-aws folder
        self.add_osbot_utils()                                              # add osbot-utils folder
        self.update()                                                       # zip files up and update lambda
        return self

