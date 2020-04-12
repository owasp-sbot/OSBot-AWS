import os

#todo: use AWS Lambda Layers
from osbot_aws.apis.S3 import S3
from osbot_utils.utils.Files import Files, folder_exists, folder_not_exists, folder_create, file_not_exists
from osbot_utils.utils.Process import Process


def load_dependencies(targets):
    for target in targets.split(','):
        load_dependency(target.strip())


def load_dependency(target):
    if os.getenv('AWS_REGION') is None:
        return

    from osbot_aws.apis.S3 import S3
    import shutil
    import sys
    s3         = S3()
    s3_bucket  = 'gw-bot-lambdas'
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


def pip_install_dependency(target):
    path_lambda_dependencies = Files.path_combine('.', '../../../_lambda_dependencies/')
    folder_create(path_lambda_dependencies)
    path_install = Files.path_combine(path_lambda_dependencies, target)
    if folder_not_exists(path_install):
        return Process.run('pip3', ['install','-t',path_install,target])
    return folder_exists(path_install)

#todo: also support AWS Lambda Layers
def upload_dependency(target):
    s3        = S3()
    s3_bucket = 'gw-bot-lambdas'
    s3_file   = 'lambdas-dependencies/{0}.zip'.format(target)
    path_libs = Files.path_combine('../../../_lambda_dependencies/', target)
    if Files.not_exists(path_libs):
        raise Exception(f"In Lambda upload_dependency, could not find dependency for: {target} , which resolved to {path_libs}")
    s3.folder_upload(path_libs, s3_bucket, s3_file)
    return s3.file_exists(s3_bucket, s3_file)