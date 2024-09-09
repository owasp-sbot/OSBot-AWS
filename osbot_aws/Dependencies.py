import os
from osbot_aws.aws.s3.S3                            import S3
from osbot_aws.AWS_Config                           import AWS_Config
from osbot_utils.decorators.methods.cache_on_self   import cache_on_self
from osbot_utils.utils.Files                        import Files, folder_exists, folder_not_exists, folder_create, file_not_exists
from osbot_utils.utils.Process                      import Process

# todo: move to lambdas_ section (since this is used by lambdas to dynamically load dependencies from zip files in s3)

class Dependencies:

    @cache_on_self
    def s3(self):
        return S3()

    def load_dependencies(self, targets):
        if type(targets) is list:
            for target in targets:
                self.load_dependency(target)
            return
        for target in targets.split(','):
            self.load_dependency(target.strip())

    def load_dependency(self, target):
        if os.getenv('AWS_REGION') is None:
            return

        import shutil
        import sys
        s3         = self.s3()
        s3_bucket  = AWS_Config().lambda_s3_bucket()
        s3_key     = 'lambdas-dependencies/{0}.zip'.format(target)
        tmp_dir    = Files.path_combine('/tmp/lambdas-dependencies', target)
        #return s3.file_exists(s3_bucket,s3_key)

        if s3.file_exists(s3_bucket,s3_key) is False:
            raise Exception("In Lambda load_dependency, could not find dependency for: {0}".format(target))

        if file_not_exists(tmp_dir):                                # download dependency
            zip_file = s3.file_download(s3_bucket, s3_key,False)    # download zip file with dependencies
            shutil.unpack_archive(zip_file, extract_dir = tmp_dir)  # unpack them
        if tmp_dir not in sys.path:                                 # if not currently in the path
            sys.path.append(tmp_dir)                                # add tmp_dir to the path that python uses to check for dependencies
        return Files.exists(tmp_dir)

    def pip_install_dependency(self, target, target_aws_lambda=True):
        path_lambda_dependencies = Files.path_combine('.', '../../../_lambda_dependencies/')
        folder_create(path_lambda_dependencies)
        path_install = Files.path_combine(path_lambda_dependencies, target)
        if folder_not_exists(path_install):
            args = ['install']
            if target_aws_lambda:
                args.extend(['--platform','manylinux1_x86_64', '--only-binary=:all:'])
            args.extend(['-t', path_install, target])
            return Process.run('pip3', args)
        return folder_exists(path_install)

    def upload_dependency(self, target):
        s3        = self.s3()
        s3_bucket = AWS_Config().lambda_s3_bucket()
        s3_file   = 'lambdas-dependencies/{0}.zip'.format(target)
        path_libs = Files.path_combine('../../../_lambda_dependencies/', target)
        if Files.not_exists(path_libs):
            raise Exception(f"In Lambda upload_dependency, could not find dependency for: {target} , which resolved to {path_libs}")
        s3.folder_upload(path_libs, s3_bucket, s3_file)
        return s3.file_exists(s3_bucket, s3_file)

# todo refactor into class (see Lambda_Upload_Package})

# LEGACY METHODS
def load_dependencies(targets):
    Dependencies().load_dependencies(targets)

def load_dependency(target):
    Dependencies().load_dependency(target)

def pip_install_dependency(target, target_aws_lambda=True):
    Dependencies().pip_install_dependency(target, target_aws_lambda)

def upload_dependency(target):
    Dependencies().upload_dependency(target)
