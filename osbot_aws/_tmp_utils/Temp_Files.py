import shutil


class Temp_Files:

    @staticmethod
    def folder_copy(source, destination,ignore=None):
        return shutil.copytree(src=source, dst=destination, ignore=ignore)