from osbot_utils.helpers.Safe_Id                                                    import Safe_Id
from osbot_aws.AWS_Config                                                           import AWS_Config
from osbot_aws.aws.lambda_.schemas.Safe_Str__File__Path__Python_Package             import Safe_Str__File__Path__Python_Package
from osbot_aws.aws.lambda_.schemas.Safe_Str__File__Name__Python_Package             import Safe_Str__File__Name__Python_Package
from osbot_aws.aws.lambda_.schemas.Schema__Lambda__Dependency__Local_Install__Data  import Schema__Lambda__Dependency__Local_Install__Data
from osbot_utils.utils.Json                                                         import json_file_load, json_file_save
from osbot_utils.helpers.safe_str.Safe_Str__File__Path                              import Safe_Str__File__Path
from osbot_utils.helpers.duration.decorators.capture_duration                       import capture_duration
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.utils.Files                                                        import path_combine, files_list__virtual_paths, file_exists, file_delete, folder_delete_recursively, current_temp_folder, create_folder
from osbot_utils.utils.Process                                                      import Process

DEFAULT__BASE_FOLDER                      = Safe_Str__File__Path(current_temp_folder())
FOLDER_NAME__LAMBDA_DEPENDENCIES_STORAGE  = Safe_Id('osbot-aws__lambda-dependencies-storage')

class Lambda__Dependency__Local(Type_Safe):
    aws_config       : AWS_Config
    base_folder      : Safe_Str__File__Path                  = DEFAULT__BASE_FOLDER
    package_name     : Safe_Str__File__Name__Python_Package  = None
    target_aws_lambda: bool                                  = True

    # Lambda__Dependencies__Storage methods
    def local__folder__bucket(self):
        return path_combine(self.local__folder__lambda_dependencies_storage(), self.s3__bucket__name())

    def local__folder__lambda_dependencies_storage(self):
        return path_combine(self.base_folder, FOLDER_NAME__LAMBDA_DEPENDENCIES_STORAGE)

    def s3__bucket__name(self):
        return self.aws_config.lambda_s3_bucket()

    def local__dependency__delete(self):
        dependency_folder__delete = folder_delete_recursively(self.local__dependency__path())
        install_data_file__delete = self.local__dependency__install__data__delete()
        return dependency_folder__delete and install_data_file__delete

    def local__dependency__exists(self):
        return self.local__dependency__install__data__exists()

    def local__dependency__files(self):
        return files_list__virtual_paths(self.local__dependency__path())

    def local__dependency__install(self):
        local_install_data = self.local__dependency__install__data()
        if local_install_data is None:
            with capture_duration() as duration__install:
                target_path = self.local__dependency__path()
                args = ['install']
                if self.target_aws_lambda:
                    args.extend(['--platform','manylinux1_x86_64', '--only-binary=:all:'])
                args.extend(['-t', target_path, self.package_name])
                install_data  = Process.run('pip3', args)
                installed_files = self.local__dependency__files()
            kwargs = dict(package_name       = self.package_name        ,
                          target_path        = target_path              ,
                          install_data       = install_data             ,
                          installed_files    = installed_files          ,
                          duration           = duration__install.seconds)

            local_install_data = Schema__Lambda__Dependency__Local_Install__Data (**kwargs)
            self.local__dependency__install__data__save(local_install_data)
        return local_install_data

    def local__dependency__install__data(self) -> Schema__Lambda__Dependency__Local_Install__Data:
        if self.local__dependency__install__data__exists():
            json_data   = json_file_load(self.local__dependency__install__data__path())
            local_install_data = Schema__Lambda__Dependency__Local_Install__Data.from_json(json_data)
            return local_install_data

    def local__dependency__install__data__delete(self) -> bool:
        return file_delete(self.local__dependency__install__data__path())

    def local__dependency__install__data__exists(self) -> bool:
        return file_exists(self.local__dependency__install__data__path())

    def local__dependency__install__data__path(self) -> Safe_Str__File__Path:
        return self.local__dependency__path() + ".json"

    def local__dependency__install__data__save(self, local_install_data: Schema__Lambda__Dependency__Local_Install__Data) -> Safe_Str__File__Path:
        json_data = local_install_data.json()
        file_path = self.local__dependency__install__data__path()
        return json_file_save(json_data, path=file_path)

    def local__dependency__path(self) -> Safe_Str__File__Path__Python_Package:
        local__dependency__path = path_combine(self.local__folder__bucket(), self.package_name)
        return Safe_Str__File__Path__Python_Package(local__dependency__path)


    def setup(self):
        create_folder(self.local__folder__bucket())
        return self