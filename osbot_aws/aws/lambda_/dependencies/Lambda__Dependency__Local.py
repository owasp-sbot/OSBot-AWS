from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency__Base                    import Lambda__Dependency__Base
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id                  import Safe_Id
from osbot_utils.utils.Zip                                                          import zip_folder_to_bytes
from osbot_aws.aws.lambda_.schemas.Safe_Str__File__Path__Python_Package             import Safe_Str__File__Path__Python_Package
from osbot_aws.aws.lambda_.schemas.Schema__Lambda__Dependency__Local_Install__Data  import Schema__Lambda__Dependency__Local_Install__Data
from osbot_utils.utils.Json                                                         import json_file_load, json_file_save
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path      import Safe_Str__File__Path
from osbot_utils.helpers.duration.decorators.capture_duration                       import capture_duration
from osbot_utils.utils.Files                                                        import path_combine, files_list__virtual_paths, file_exists, file_delete, folder_delete_recursively, current_temp_folder, create_folder
from osbot_utils.utils.Process                                                      import Process

FOLDER_NAME__LAMBDA_DEPENDENCIES_STORAGE  = Safe_Id('osbot-aws__lambda-dependencies-storage')

class Lambda__Dependency__Local(Lambda__Dependency__Base):
    target_aws_lambda: bool = True                                      # todo: rename this var to a better name

    def base_folder(self):
        return self.temp_folder

    def folder__bucket(self):
        return path_combine(self.folder__lambda_dependencies_storage(), self.s3__bucket__name())

    def folder__lambda_dependencies_storage(self):
        return path_combine(self.base_folder(), FOLDER_NAME__LAMBDA_DEPENDENCIES_STORAGE)

    def s3__bucket__name(self):
        return self.aws_config.lambda_s3_bucket()

    def delete(self):
        dependency_folder__delete = folder_delete_recursively(self.path())
        install_data_file__delete = self.install__data__delete()
        return dependency_folder__delete and install_data_file__delete

    def exists(self):
        return self.install__data__exists()

    def files(self):
        return files_list__virtual_paths(self.path())

    def files__zipped(self):
        root_dir        = self.path()
        files_to_ignore = '.DS_Store'
        return zip_folder_to_bytes(root_dir=root_dir, files_to_ignore=files_to_ignore)


    def install(self):
        local_install_data = self.install__data()
        if local_install_data is None:
            with capture_duration() as duration__install:
                target_path = self.path()
                args = ['install']
                if self.target_aws_lambda:
                    args.extend(['--platform','manylinux1_x86_64', '--only-binary=:all:'])
                args.extend(['-t', target_path, self.package_name])
                install_data  = Process.run('pip3', args)
                installed_files = self.files()
            kwargs = dict(package_name       = self.package_name        ,
                          target_path        = target_path              ,
                          install_data       = install_data             ,
                          installed_files    = installed_files          ,
                          duration           = duration__install.seconds)

            local_install_data = Schema__Lambda__Dependency__Local_Install__Data (**kwargs)
            self.install__data__save(local_install_data)
        return local_install_data

    def install__data(self) -> Schema__Lambda__Dependency__Local_Install__Data:
        if self.install__data__exists():
            json_data   = json_file_load(self.install__data__path())
            local_install_data = Schema__Lambda__Dependency__Local_Install__Data.from_json(json_data)
            return local_install_data

    def install__data__delete(self) -> bool:
        return file_delete(self.install__data__path())

    def install__data__exists(self) -> bool:
        return file_exists(self.install__data__path())

    def install__data__path(self) -> Safe_Str__File__Path:
        return self.path() + ".json"

    def install__data__save(self, local_install_data: Schema__Lambda__Dependency__Local_Install__Data) -> Safe_Str__File__Path:
        json_data = local_install_data.json()
        file_path = self.install__data__path()
        return json_file_save(json_data, path=file_path)

    def path(self) -> Safe_Str__File__Path__Python_Package:
        local__dependency__path = path_combine(self.folder__bucket(), self.package_name)
        return Safe_Str__File__Path__Python_Package(local__dependency__path)



    def setup(self):
        create_folder(self.folder__bucket())
        return self