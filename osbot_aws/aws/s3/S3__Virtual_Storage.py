from typing                                                             import List, Optional, Dict, Any
from osbot_aws.aws.s3.S3__DB_Base                                       import S3__DB_Base
from osbot_utils.decorators.methods.cache_on_self                       import cache_on_self
from osbot_utils.helpers.llms.cache.Virtual_Storage__Local__Folder      import Virtual_Storage__Local__Folder
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                  import Safe_Str__File__Path
from osbot_utils.utils.Files                                            import path_combine_safe

VIRTUAL_STORAGE__DEFAULT__ROOT_FOLDER = Safe_Str__File__Path("s3-virtual-storage/")

class Virtual_Storage__S3(Virtual_Storage__Local__Folder):                                          # Storage implementation using AWS S3 as the backend."""
    root_folder: Safe_Str__File__Path = VIRTUAL_STORAGE__DEFAULT__ROOT_FOLDER                     # Prefix for all stored files in S3
    s3_db      :  S3__DB_Base

    def bucket_name(self):
        return self.s3_db.s3_bucket()

    def folder__create(self, path_folder) -> None:                                                  # Folders don't need to be explicitly created in S3.
        pass                                                                                        # S3 has no concept of folders, they're created implicitly with object keys

    def json__load(self, path: Safe_Str__File__Path) -> Optional[Dict[str, Any]]:                   # Load JSON data from S3
        s3_key = self.get_s3_key(path)
        if self.file__exists(path):
            json_data = self.s3_db.s3_file_contents_json(s3_key)
            return json_data
        return None

    def json__save(self, path: Safe_Str__File__Path, data: dict) -> bool:           # Save JSON data to S3
        s3_key      = self.get_s3_key(path)
        result      = self.s3_db.s3_save_data(data=data, s3_key=s3_key)
        return result is not None

    def get_full_path(self, path: Safe_Str__File__Path) -> Safe_Str__File__Path:    # For S3, we don't need physical paths, but we maintain the same interface.
        return path

    def get_s3_key(self, path: Safe_Str__File__Path) -> str:                        # Convert the virtual path to an S3 key with proper prefix.
        if str(path).startswith(str(self.root_folder)):
            return str(path)
        return path_combine_safe(self.root_folder, path)

    def file__delete(self, path: Safe_Str__File__Path) -> bool:             # Delete a file from S3.
        s3_key = self.get_s3_key(path)
        return self.s3_db.s3_file_delete(s3_key)

    def file__exists(self, path: Safe_Str__File__Path) -> bool:             # Check if file exists in S3.
        s3_key = self.get_s3_key(path)
        return self.s3_db.s3_file_exists(s3_key)

    def files__all(self, full_path=False) -> List[str]:                                      # List all files in S3 with the specified prefix.
        prefix = str(self.root_folder)
        if prefix.endswith('/'):                                                             # todo: handle bug in s3_folder_files__all which will lost the first char if the folder path ends with an /
            prefix = prefix[:-1]
        all_objects = self.s3_db.s3_folder_files__all(folder=prefix, full_path=full_path)
        return all_objects

    @cache_on_self
    def path_folder__root_cache(self) -> str:                               # In S3 storage, this is a virtual concept.
        return str(self.root_folder)

    def clear_all(self) -> bool:                                            # Clear all stored files in this virtual storage.
        raise NotImplemented("not implemented since this is quite a dangerous method")

    # # todo: check for the performance impact (and costs) of this method
    # def stats(self) -> Dict[str, Any]:                                      # Get storage statistics.
    #
    #     files = self.files__all(full_path=True)
    #     total_size = 0
    #
    #     for file_path in files:
    #         file_info = self.s3_db.s3_file_info(file_path)
    #         if file_info and 'ContentLength' in file_info:
    #             total_size += file_info['ContentLength']
    #
    #     return { "storage_type"    : "s3"                   ,
    #              "bucket_name"     : self.s3_db.s3_bucket() ,
    #              "prefix"          : self.root_folder       ,
    #              "file_count"      : len(files)             ,
    #              "total_size_bytes": total_size             }